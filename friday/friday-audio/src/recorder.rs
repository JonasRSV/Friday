pub trait Recorder {
    fn sample_rate(&self) -> u32;
    fn read(&self) -> Option<Vec<i16>>;
}

