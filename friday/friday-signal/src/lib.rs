use friday_error::FridayError;
use friday_logging;
use std::rc::Rc;
use std::cell::RefCell;
pub mod core;
pub mod mock;

pub struct Composer {
    devices: Vec<Rc<RefCell<dyn core::Device>>>
}

impl Composer {
    pub fn new() -> Result<Composer, FridayError> {
        Ok(Composer{
            devices: Vec::new()
        })
    }

    pub fn register_devices(&mut self, devices: Vec<Rc<RefCell<dyn core::Device>>>) {
        self.devices.extend(devices.iter().cloned());
    }

    pub fn send(&self, signal: &core::Signal) {
        for device in self.devices.iter() {
            let name = device.borrow().name();
            match device.borrow_mut().send(signal) {
                Err(err) => friday_logging::error!("Sending {:?} on {} gave error {:?}", 
                    signal, name, err),
                Ok(()) => friday_logging::debug!("Sent {:?} on {}", signal, name)
            }
        }
    }
}


