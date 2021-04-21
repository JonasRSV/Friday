use crate::core::SpeakDetector;
use serde_derive::{Deserialize, Serialize};

use friday_storage;
use friday_logging;
use friday_error::{FridayError, propagate};

#[derive(Deserialize, Serialize)]
struct Config {
    min_peaks: u32,
    min_peak_height: i16,

    // Will print the peaks heigher than min_peak_height and the heighest peak 
    verbose: Option<bool>
}

pub struct PeakBasedDetector {
    min_peaks: u32,
    min_peak_height: i16,
    verbose: bool
}

impl PeakBasedDetector {
    fn peaks(audio: &Vec<i16>, min_peak_height: i16, verbose: bool) -> u32 {

        let mut p = 0;
        let mut max_p: i16 = 0;
        for sample in audio.iter() {
            let height = i16::abs(*sample);

            if height > min_peak_height {
                p += 1;
            }
            
            if height > max_p {
                max_p = height;
            }

        }

        if verbose {
            friday_logging::debug!("Max peak {}, peaks > {}: {}", max_p, min_peak_height, p);
        }

        return p;
    }

    pub fn new() -> Result<PeakBasedDetector, FridayError> {
        friday_storage::config::get_config("vad_peaks.json").map_or_else(
            propagate!("Failed to initialize Peak based VAD"),
            |config: Config| Ok(PeakBasedDetector::from_config(config)))
    }

    fn from_config(config: Config) -> PeakBasedDetector {
        PeakBasedDetector {
            min_peaks: config.min_peaks,
            min_peak_height: config.min_peak_height,
            verbose: match config.verbose {
                None => false,
                Some(v) => v
            }
        }

    }
}

impl SpeakDetector for PeakBasedDetector {
    fn detect(&mut self, audio: &Vec<i16>) -> bool {
        let peaks = PeakBasedDetector::peaks(audio, self.min_peak_height, self.verbose);
        return peaks > self.min_peaks;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn peak_based_detector() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        
        let config_dir = friday_storage::config::get_config_directory().unwrap();
        let files = friday_storage::files::Files::new(config_dir).unwrap();

        let (quiet_audio, _) = files.read_audio("silence.wav").unwrap();
        let (voice_audio, _) = files.read_audio("voice.wav").unwrap();


        let mut detector = PeakBasedDetector::from_config(Config{
            min_peaks: 3,
            min_peak_height: 4000,
            verbose: Some(true)
        });

        assert!(detector.detect(&voice_audio));
        assert!(!detector.detect(&quiet_audio));
    }
}
