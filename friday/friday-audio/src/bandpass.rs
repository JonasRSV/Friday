use friday_error::FridayError;
use friday_logging;

 pub struct FIR {
     a: Vec<f64>,
     b: Vec<f64>
 }

impl FIR {
    pub fn new() -> Result<FIR, FridayError> {
        // coefficients taken from a python script..
        // TODO: generate coefficients myself somehow.
        Ok(FIR {
            // make sure a[0] is 1 otherwise we must normalize
            a: vec![1.0, -4.69088118, 9.74727249, 
                    -1.24296500e+01, 1.14718272e+01, -8.13237600, 
                    4.26696308, -1.58918360, 4.30296808e-01, 
                    -7.87855705e-02, 4.67933063e-03],

            b: vec![0.03489971, 0.0, -0.17449857, 
                    0.0, 0.34899715, 0.0, 
                    -0.34899715, 0.0, 0.17449857, 
                    0.0, -0.03489971]
        })
    }


    /// runs bandpass on audio and return smoothed vector
    /// Implementation from 
    /// https://github.com/scipy/scipy/blob/v1.6.2/scipy/signal/signaltools.py#L1842-L2032
    pub fn pass(&self, audio: &Vec<i16>) -> Vec<i16>  {
        let mut result: Vec<f64> = vec![0.0; audio.len()];
        for i in 0..audio.len() {
            let mut n: f64 = audio[i] as f64 * self.b[0];
            let r = std::cmp::min(self.a.len(), i);
            for j in 1..r {
                n += (self.b[j] * audio[i - j] as f64) - (self.a[j] * result[i - j]);
            }

            result[i] = n.clone();
        }


        return result.iter().map(|v| v.clone() as i16).collect();
    }
}
