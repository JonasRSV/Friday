

pub trait SpeakDetector {
    fn detect(&mut self, audio: &Vec<i16>) -> bool;
}

pub struct EnergyBasedDetector {
    energy_threshold: f64,
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

    pub fn new(threshold: f64) -> EnergyBasedDetector {
        return EnergyBasedDetector {
            energy_threshold: threshold,
        }
    }
}

impl SpeakDetector for EnergyBasedDetector {
    fn detect(&mut self, audio: &Vec<i16>) -> bool {
        let energy = EnergyBasedDetector::energy(audio);
        //println!("Energy threshold {} -- Energy {}", self.energy_threshold, energy);
        return energy > self.energy_threshold;
    }
}


#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
