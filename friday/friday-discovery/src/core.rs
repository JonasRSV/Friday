use friday_error::FridayError;
use std::time::Duration;

pub enum Blip {
    Ok
}

pub trait LightHouse {
    fn name(&self) -> String;
    // This is an approximate time since if other lighthouses
    // takes up much time this cannot be guaranteed.
    fn time_between_blip(&self) -> Duration;
    fn blip(&mut self) -> Result<Blip, FridayError>;
}
