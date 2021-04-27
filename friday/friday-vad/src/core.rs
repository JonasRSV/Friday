pub enum VADResponse {
    Voice,
    Silence,
}

pub trait SpeakDetector {
    fn detect(&mut self, audio: &Vec<i16>) -> VADResponse;
}
