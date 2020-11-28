
#[derive(Clone)]
pub struct RecordingConfig {
    pub sample_rate: u32,
    pub buffer_size: u32,
    pub model_frame_size: usize
}


pub mod friday_cpal; 
pub mod friday_alsa;
pub mod recorder;


