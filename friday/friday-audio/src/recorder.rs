use crate::RecordingConfig;
use friday_error::FridayError;

pub trait Recorder {
    fn read(&self) -> Option<Vec<i16>>;
    fn record(conf: &RecordingConfig) -> Result<Box<Self>, FridayError>;
}
