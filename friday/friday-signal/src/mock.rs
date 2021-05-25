use friday_error::FridayError;
use friday_logging;
use crate::core::{Signal, Device};

pub struct MockDevice;

impl MockDevice {
    pub fn new() -> MockDevice {
        MockDevice{}
    }
}

impl Device for MockDevice {
    fn name(&self) -> String { "mock".to_owned() }
    fn send(&mut self, signal: &Signal) -> Result<(), FridayError> {
        friday_logging::debug!("Sending signal {:?}", signal);
        Ok(())
    }
}

pub struct SilentMockDevice;

impl SilentMockDevice {
    pub fn new() -> SilentMockDevice {
        SilentMockDevice{}
    }
}


impl Device for SilentMockDevice {
    fn name(&self) -> String { "SilentMock".to_owned() }
    fn send(&mut self, _: &Signal) -> Result<(), FridayError> {
        Ok(())
    }
}
