
#[derive(Clone)]
pub struct RecordingConfig {
    pub sample_rate: u32,
    pub model_frame_size: usize,

    // constant that each sample is multiplied with
    pub loudness: i16
        
}


pub mod friday_cpal; 
pub mod friday_alsa;
pub mod recorder;


