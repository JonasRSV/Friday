use crate::core::SpeakDetector;
use serde_derive::{Deserialize, Serialize};

use friday_storage;
use friday_error::{FridayError, propagate};

#[derive(Deserialize, Serialize)]
struct Config {
    threshold: f64,

    // Will print the energy if provided and is true
    verbose: Option<bool>
}

pub struct EnergyBasedDetector {
    energy_threshold: f64,
    verbose: bool
}

impl EnergyBasedDetector {
    fn energy(audio: &Vec<i16>) -> f64 {
        let mut e = 0.0;
        for sample in audio.iter() {
            let f64sample = sample.clone() as f64;
            e += f64::sqrt(f64sample * f64sample);
        }
        return e / audio.len() as f64;
    }

    pub fn new() -> Result<EnergyBasedDetector, FridayError> {
        friday_storage::config::get_config("vad_energy.json").map_or_else(
            propagate!("Failed to initialize EnergyBased VAD"),
            |config: Config| Ok(EnergyBasedDetector {
                energy_threshold: config.threshold,
                verbose: match config.verbose {
                    None => false,
                    Some(v) => v
                }
            }))
    }
}

impl SpeakDetector for EnergyBasedDetector {
    fn detect(&mut self, audio: &Vec<i16>) -> bool {
        let energy = EnergyBasedDetector::energy(audio);

        if self.verbose {
            println!("Energy threshold {} -- Energy {}", self.energy_threshold, energy);
        }

        return energy > self.energy_threshold;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn energy_based_detector() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let noisy_audio = vec![16000; 16000];
        let quiet_audio = vec![0; 16000];

        let mut detector = EnergyBasedDetector::new().expect("Failed to create EnergyBasedDetector");

        assert!(detector.detect(&noisy_audio));
        assert!(!detector.detect(&quiet_audio));
    }
}
