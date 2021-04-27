use friday_error::FridayError;

pub trait Recorder {
    fn sample_rate(&self) -> u32;
    fn read(&self) -> Option<Vec<i16>>;
    fn clear(&self) -> Result<(), FridayError>;
}

