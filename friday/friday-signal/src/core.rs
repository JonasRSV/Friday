use friday_error::FridayError;

#[derive(Debug)]
pub enum Listening {
    Start,
    Stop
}

#[derive(Debug)]
pub enum Inference {
    Start,
    Stop
}

#[derive(Debug)]
pub enum Dispatch {
    Start,
    Stop
}


#[derive(Debug)]
pub enum Signal {
    // States of the main thread
    Listening(Listening),
    Inference(Inference),
    Dispatch(Dispatch)

}

pub trait Device {
    fn name(&self) -> String;
    fn send(&mut self, signal: &Signal) -> Result<(), FridayError>;
}

