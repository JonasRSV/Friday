use friday_error::FridayError;


#[derive(Debug)]
pub enum Signal {

    // States of the main thread
    StartListening,
    StopListening,

    StartInferring,
    StopInferring,

    StartDispatching,
    StopDispatching
        

}

pub trait Device {
    fn name(&self) -> String;
    fn send(&mut self, signal: &Signal) -> Result<(), FridayError>;
}

