use friday_error::{FridayError, propagate};
use friday_storage;
use std::sync::{Arc, RwLock, Mutex};
use std::sync::atomic;

use std::thread;

use std::collections::BinaryHeap;

use serde_derive::{Deserialize, Serialize};
use crate::ping_site::PingSite;
use crate::core::LightHouse;
use std::cmp::Ordering;

use std::time;

#[derive(Serialize, Deserialize, Clone, Debug)]
struct DiscoveryConfig {
    name: String
}

#[derive(Clone)]
struct Task {
    time: u64,
    lighthouse: Arc<Mutex<dyn LightHouse>>,
}

impl Ord for Task {
    fn cmp(&self, other: &Self) -> Ordering {
        // We have not here to make our heap into a min-heap instead of a max-heap
        match self.time.cmp(&other.time) {
            Ordering::Greater => Ordering::Less,
            Ordering::Less => Ordering::Greater,
            Ordering::Equal => Ordering::Equal
        }
    }
}

impl PartialOrd for Task {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Task {
    fn eq(&self, other: &Self) -> bool {
        self.time == other.time
    }
}

impl Eq for Task { }

fn system_seconds_or_exit(running: Arc<atomic::AtomicBool>) -> Option<u64> {
    loop {
        if !running.load(atomic::Ordering::Relaxed) { return None; }

        match time::SystemTime::now().duration_since(time::UNIX_EPOCH) {
            Err(err) => println!("Failed to get duration since epoch - Reason: {}", err),
            Ok(duration) => return Some(duration.as_secs())
        }



        thread::sleep(time::Duration::from_secs(2));
    }

}

pub struct DiscoveryHandle {
    handle: thread::JoinHandle<()>,
    running: Arc<atomic::AtomicBool>,

        
}

impl DiscoveryHandle {
    pub fn stop(self) {
        self.running.swap(false, atomic::Ordering::Relaxed);
        self.handle.join().expect("Failed to join Discovery thread");
    }

    pub fn wait(self) {
        self.handle.join().expect("Failed to join Discovery thread");
    }
}

#[derive(Clone)]
pub struct Discovery {
    name: Arc<RwLock<String>>,
    running: Arc<atomic::AtomicBool>,
    // Port which the webserver is running on
    port: u16
}


impl Discovery {
    pub fn new(port: u16) -> Result<Discovery, FridayError> {
        friday_storage::config::get_config("discovery.json").map_or_else(
            propagate!("Failed to create 'Discovery'"),
            |config: DiscoveryConfig| Ok(Discovery{
                name: Arc::new(RwLock::new(config.name)),
                running: Arc::new(atomic::AtomicBool::new(false)),
                port
            }))
    }

    pub fn make_discoverable(&self) -> DiscoveryHandle {
        let self_reference = Box::new(self.clone());

        // Set running to true
        self.running.swap(true, atomic::Ordering::Relaxed);

        // Start light houses
        let handle = thread::spawn( move || { 
            Discovery::run_lighthouses(self_reference);
        });

        return DiscoveryHandle {
            handle,
            running: self.running.clone()
        };
    }

    fn execute_task(running: Arc<atomic::AtomicBool>, task: Task) -> Option<Task> {
        let time_between_blip = match task.lighthouse.lock() {
            Err(err) => {
                println!("Failed to aquire lock for task.. - Reason: {} \nContinuing..",
                    err);
                // Try again in 5 seconds..
                5
            },
            Ok(mut lighthouse) => 
                match lighthouse.blip() {
                    Ok(_) => lighthouse.time_between_blip().as_secs(),
                    Err(err) => {
                        // TODO: Maybe remove this..? If it is too verbose
                        println!("\n---------------------------\n\
                            Discovery Error {:?} \n on blip of {}\
                            \n---------------------------\n", 
                            err, 
                            lighthouse.name());

                        // Try again in 5 seconds..
                        5
                    }            
                }
        };

        return match system_seconds_or_exit(running) {
            Some(time) => Some(Task {
                time: time + time_between_blip,
                lighthouse: task.lighthouse
            }),
            None => None
        }
    }

    fn run_lighthouses(discovery: Box<Discovery>) {
        let mut lighthouses: Vec<Arc<Mutex<dyn LightHouse>>> = Vec::new();

        PingSite::new(discovery.name.clone(), discovery.port).map_or_else(
            |err| println!("Failed to create 'PingSite' Lighthouse - Reason: {:?}", err),
            |ping_site| lighthouses.push(Arc::new(Mutex::new(ping_site))));

        let mut priority_queue = BinaryHeap::<Task>::new();

        for lighthouse in lighthouses.iter() {
            match system_seconds_or_exit(discovery.running.clone()) {
                Some(time) => priority_queue.push(
                    Task{
                        time,
                        lighthouse: lighthouse.clone()
                    }),
                None => return ()
            }
        }

        loop {
            match system_seconds_or_exit(discovery.running.clone()) {
                Some(secs) => {
                    match priority_queue.pop() {
                        Some(task) => {
                            let task_time = task.time;
                            if secs < task_time {
                                // Sleep until first task is ready
                                println!("Discovery Sleeping for {} seconds", task_time - secs);
                                thread::sleep(time::Duration::from_secs(task_time - secs));
                            }

                            match Discovery::execute_task(discovery.running.clone(), task) {
                                Some(new_task) => priority_queue.push(new_task),
                                None => break
                            }
                        }

                        None => break
                    }
                },
                None => break
            }
        }
    }
}
