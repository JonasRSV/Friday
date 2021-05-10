use serde_derive::{Deserialize, Serialize};
use friday_error::{FridayError, propagate};


#[derive(Deserialize, Serialize)]
pub struct RecordingStorage {
    pub loudness: i16,
    pub device: Option<String>
}

#[derive(Clone, )]
pub struct RecordingConfig {
    pub sample_rate: u32,
    pub model_frame_size: usize,

    // constant that each sample is multiplied with
    pub loudness: i16,

    pub device: String


        
}

impl RecordingConfig {
    pub fn new(
        sample_rate: u32, 
        model_frame_size: usize) -> Result<RecordingConfig, FridayError> {
        friday_storage::config::get_config("recording.json").map_or_else(
            propagate!("Failed to create recording config"),
            |config: RecordingStorage| 
                Ok(RecordingConfig {
                    sample_rate,
                    model_frame_size,
                    loudness: config.loudness,
                    device: config.device.unwrap_or("default".to_owned())
                        
                })
        )
    }
}


pub mod friday_cpal; 
pub mod friday_alsa;
pub mod recorder;
pub mod web;


