use crate::core;
use crate::core::Karta;
use std::cmp::Ordering;
use std::sync::{Arc, Mutex};

use std::collections::BinaryHeap;
use std::time;

pub enum Status {
    Ready,
    Next(time::Duration),
    NoTask
}

#[derive(Clone)]
struct Task {
    time: u64,
    karta: Arc<Mutex<dyn Karta>>,
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

#[derive(Clone)]
pub struct Manager {
    priority_queue: BinaryHeap<Task>
}

impl Manager {
    pub fn new() -> Manager {
        Manager {
            priority_queue: BinaryHeap::new()
        }
    }

    pub fn setup(&mut self, kartor: Vec<Arc<Mutex<dyn Karta>>>) -> Self {
        // We set time 0 so that we execute all kartor in the 
        // beginning.
        for karta in kartor {
            self.priority_queue.push(Task{
                time: 0,
                karta
            })
        }

        return self.clone();
    }

    pub fn status(&self, timestamp: u64) -> Status {
        match self.priority_queue.peek() {
            Some(task) => if task.time < timestamp { 
                Status::Ready 
            } else { 
                Status::Next(time::Duration::from_secs(task.time - timestamp))
            },
            None => Status::NoTask
        }
    }

    pub fn exec(&mut self) -> core::Status<Arc<Mutex<dyn Karta>>> {
        let maybe_task = self.priority_queue.pop();

        match maybe_task {
            Some(task) => match task.karta.lock() {
                Err(err) => {
                    println!("Failed to aquire lock for task.. - Reason: {}", err);
                    core::Status::Retry(task.karta.clone(), time::Duration::from_secs(5))
                },
                Ok(mut karta) => match karta.clue() {
                    Ok(_) => core::Status::Continue(task.karta.clone()),
                    Err(err) => {
                        // TODO: Maybe remove this..? If it is too verbose
                        println!("\n---------------------------\n\
                                Discovery Error {:?} \n on clue from {}\
                                \n---------------------------\n", 
                                err, 
                                karta.name());
                        core::Status::Retry(task.karta.clone(), time::Duration::from_secs(5))

                    }
                }
            },
            None => core::Status::Exit
        }
    }

    pub fn add(&mut self, karta: Arc<Mutex<dyn Karta>>, timestamp: u64) {
        self.priority_queue.push(
            Task{
                karta,
                time: timestamp
            })
    }
}
