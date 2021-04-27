use friday_error::FridayError;
use friday_logging;
use crate::core::{Signal, Device};

pub struct MockDevice;

impl Device for MockDevice {
    fn name(&self) -> String { "mock".to_owned() }
    fn send(&mut self, signal: &Signal) -> Result<(), FridayError> {
        friday_logging::debug!("Sending {:?} Listening..", signal);

        Ok(())
    }
}


