use friday_error::{FridayError, propagate};
use friday_storage;
use friday_logging;
use std::sync::{Arc, RwLock, Mutex};
use std::sync::atomic;

use std::thread;


use serde_derive::{Deserialize, Serialize};

use crate::core;
use crate::core::Karta;
use crate::karta_site::KartaSite;
use crate::task_manager;

use std::time;

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

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct DiscoveryConfig {
    pub name: String
}

#[derive(Clone)]
pub struct Discovery {
    pub name: Arc<RwLock<String>>,
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

    /// Starts a thread that leaves clues to make it easier for users to find Friday.
    pub fn make_discoverable(&self) -> DiscoveryHandle {
        let self_reference = Box::new(self.clone());

        // Set running to true
        self.running.swap(true, atomic::Ordering::Relaxed);

        // Start serving clues using the maps 'Kartor' 
        let handle = thread::spawn( move || { 
            Discovery::start(self_reference);
        });

        return DiscoveryHandle {
            handle,
            running: self.running.clone()
        };
    }

    fn poll_for(&self, duration: time::Duration) -> core::Status<()> {
        // This lets the thread 'sleep' using polling so that the discovery is exitable
        // otherwise if the main thread sends signal to stop.. if we're using just 'sleep'
        // this thread wont stop until sleep is over. If this thread is supposed to sleep for
        // say 10 minutes - it kind of sux to have to wait 10 minutes for the program to exit.

        friday_logging::info!("Discovery - Polling for {} seconds", duration.as_secs());

        let poll_until = time::Instant::now() + duration;
        loop {
            // We recieve a signal to stop so we return exit
            if !self.running.load(atomic::Ordering::Relaxed) { return core::Status::Exit; }

            thread::sleep(time::Duration::from_secs(2));

            if time::Instant::now() > poll_until {
                break
            }
        }

        // If we did not recieve a signal to stop we just return continue
        core::Status::Continue(())

    }

    /// Returns timestamp in seconds of time since EPOCH
    /// or returns Exit signal if a user signals us to exit before we're able to aquire that time
    pub fn get_seconds_timestamp(&self) -> core::Status<u64> {

        loop {
            if !self.running.load(atomic::Ordering::Relaxed) { return core::Status::Exit ; }
            match time::SystemTime::now().duration_since(time::UNIX_EPOCH) {
                Err(err) => friday_logging::warning!("Failed to get duration since epoch - Reason: {}", err),
                Ok(duration) => return core::Status::Continue(duration.as_secs())
            }

            // Wait two seconds before trying to get time again
            thread::sleep(time::Duration::from_secs(2));
        }
    }

    fn setup_kartor(&self) -> Vec<Arc<Mutex<dyn Karta>>> {
        let mut kartor: Vec<Arc<Mutex<dyn Karta>>> = Vec::new();


        
        // A worker that pings a site with the machines local IP
        // so that it is easy to discover - using that site.
        // The site provides an UI that will list all available UIs on the 
        // local network
        KartaSite::new(self.name.clone(), self.port).map_or_else(
            // If we are unable to create it we just log an error and continue
            // this means we can disable this karta but just not providing its config
            // this error will then say that the config was not provided to alert the user of
            // it, but friday will continue as usual and other kartas can be loaded.
            |err| friday_logging::warning!("Failed to create 'KartaSite' Karta - Reason: {:?}", err),
            |karta| kartor.push(Arc::new(Mutex::new(karta))));

        return kartor;
    }

    fn start(discovery: Box<Discovery>) {
        let mut manager = task_manager::Manager::new()
            .setup(
                discovery
                .setup_kartor());



        loop {
            let status: core::Status<()> = match discovery.get_seconds_timestamp() {
                // We were able to get current time and thus continues discovery
                core::Status::Continue(secs) => match manager.status(secs) {
                    // No task is queued - we quit discovery
                    task_manager::Status::NoTask => core::Status::Exit,

                    // Polls until next task is available
                    task_manager::Status::Next(duration) => discovery.poll_for(duration),

                    // Exec - pops and runs task
                    task_manager::Status::Ready => match manager.exec() {
                        // Task manager says we should exit - so we do
                        core::Status::Exit => core::Status::Exit,

                        // Task executed this karta and suggests we should requeue the
                        // clue in this karta, so we queue it and continue
                        core::Status::Continue(karta) => match karta.lock() {
                            Ok(guarded_karta) => {
                                manager.add(karta.clone(), secs + guarded_karta.time_to_clue().as_secs());
                                core::Status::Continue(())
                            }
                            Err(err) => {
                                friday_logging::fatal!("Failed to aquire lock for a 'Karta'\
                                    - Reason: {}",
                                    err);

                                // TODO: Currently we don't recover from poison error
                                // should add logic for creating a new lock if this happends
                                // this however should never happend.. but logic for that might
                                // be nice anyhow. There is that law about anything that can go
                                // wrong will go wrong..
                            
                                core::Status::Exit

                            }
                        },
                        // the task manager says we should retry this task in 'duration' time
                        // so we re-queue it in suggested time 
                        core::Status::Retry(karta, duration) => {
                            manager.add(karta, secs + duration.as_secs());
                            core::Status::Continue(())
                        }
                    }
                },
                // Time getting asks us to retry 'this will not happend at all in
                // the current implementation' but if it happends we just continue
                core::Status::Retry(_, _) => core::Status::Continue(()),

                // We were unable to get time and got an exit signal
                // so we exit
                core::Status::Exit => core::Status::Exit
            };

            // Break - this will exit the loop and stop the discovery thread 
            if status == core::Status::Exit {
                break;
            }
        }
    }
}
