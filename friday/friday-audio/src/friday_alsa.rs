use friday_error::FridayError;
use friday_logging;
use crate::recorder::Recorder;
use crate::RecordingConfig;

pub struct ALSAIStream;

impl ALSAIStream {
    pub fn record(_conf: &RecordingConfig) -> Result<Box<Self>, FridayError> {
        // This was mostly used to debug CPAL, since CPAL uses ALSA internally
        // but one day maybe ill just use alsa directly for some reason
        // so ill leave the code here
        for device in alsa::device_name::HintIter::new_str(None, "pcm").unwrap() {
            let name = device.name.unwrap();
            let io = device.direction;

            if let Some(io) = io {
                friday_logging::info!("device {} io: {:?}", name, io);
                if io != alsa::Direction::Capture {
                    continue;
                }
            }
            let has_available_input = {
                let capture_handle =
                    alsa::pcm::PCM::new(&name, alsa::Direction::Capture, true);
                capture_handle.is_ok()
            };

            if has_available_input {
                friday_logging::info!("Is recording device {}", name);
            }
        }

        todo!()
    }
}

impl Recorder for ALSAIStream {
    fn read(&self) -> Option<Vec<i16>> {
        todo!()
    }


    fn sample_rate(&self) -> u32 {
        8000
    }

    fn clear(&self) -> Result<(), FridayError> {
        todo!()
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn alsa_some_printing() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000,
            loudness: 1,
            device: "default".to_owned()
        };

        ALSAIStream::record(&r).expect("Failed to record with ALSAIStream");
    }
}
