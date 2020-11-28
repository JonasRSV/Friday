use std::ffi::CString;

use friday_error::frierr;
use friday_error::FridayError;
use crate::recorder::Recorder;
use crate::RecordingConfig;
use alsa::card;

pub struct ALSAIStream;

impl Recorder for ALSAIStream {
    fn read(&self) -> Option<Vec<i16>> {
        todo!()
    }

    fn record(conf: &RecordingConfig) -> Result<Box<Self>, FridayError> {
        for card in alsa::card::Iter::new() {
            println!("Card {}", card.unwrap().get_name().unwrap());
            let iface = CString::new("pcm");

            for device in alsa::device_name::HintIter::new(Some(&card.unwrap()), &iface.unwrap()).unwrap() {
                println!("Device {}", device.name.unwrap());
            }

        }

        for device in alsa::device_name::HintIter::new_str(None, "pcm").unwrap() {
            println!("Device with new_str {}", device.name.unwrap());
        }


        todo!()
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::path::Path;
    use wav;
    #[test]
    fn alsa_some_printing() {
        let r = RecordingConfig {
            sample_rate: 8000,
            buffer_size: 2000,
            model_frame_size: 16000
        };

        ALSAIStream::record(&r).expect("Failed to record with ALSAIStream");
    }

    #[test]
    fn normal_workload() {
        //let r = RecordingConfig {
            //sample_rate: 8000,
            //buffer_size: 2000,
            //model_frame_size: 16000
        //};


        //let istream = record(&r).unwrap();


        //for _ in 0..50 {
            //std::thread::sleep(std::time::Duration::from_millis(250));
            //match istream.read() {
                //Some(_) => println!("Read Ok!"),
                //_ => println!("Failed to read")
            //}

        //}

        //drop(istream.stream);
    }

    #[test]
    fn record_audio_files() {
        //let r = RecordingConfig {
            //sample_rate: 8000,
            //buffer_size: 2000,
            //model_frame_size: 16000
        //};


        //let istream = record(&r).unwrap();


        //for index in 0..8 {
            //std::thread::sleep(std::time::Duration::from_millis(2000));
            //match istream.read() {
                //Some(data) => {
                    //println!("Read Ok!");
                    //let out = File::create(
                        //Path::new(&format!("test-{}.wav", index)));

                    //match out {
                        //Ok(mut fw) => {
                            //let header = wav::Header::new(1, 1, r.sample_rate, 16);
                            //match wav::write(header, wav::BitDepth::Sixteen(data), &mut fw) {
                                //Ok(_) => println!("Successfully wrote to wav file!"),
                                //Err(e) => println!("Failed to write to wav file - Reason: {}", e)
                            //}

                        //},
                        //Err(e) => println!("Failed to create out file - Reason: {}", e)
                    //}




                //},
                //_ => println!("Failed to read")
            //}

        //}

        //drop(istream.stream);
    }
}
