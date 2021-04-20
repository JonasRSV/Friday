
pub struct MFCC {
    n_mfcc: u32,
    n_fft: u32,
    stride: u32,
    n_mels: u32
}

impl MFCC {

    pub fn new(n_mfcc: u32, n_fft: u32, stride: u32, n_mels: u32) -> MFCC {
        MFCC {
            n_mfcc,
            n_fft,
            stride,
            n_mels
        }
    }

    pub fn transform(v :&Vec<i16>) -> Vec<Vec<f32>> {
        todo!()
    }
}
