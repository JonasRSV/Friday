use cpal;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex, MutexGuard};
use circular_queue::CircularQueue;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;
use crate::recorder::Recorder;
use crate::RecordingConfig;


pub struct CPALIStream {
    config: RecordingConfig,
    _stream: cpal::Stream,
    buffer: Arc<Mutex<CircularQueue<i16>>>

}

fn write_to_buffer<T>(input: &[T], buffer: &Arc<Mutex<CircularQueue<i16>>>) 
    where T: cpal::Sample {
        fn insert<T>(samples: &[T], q: &mut MutexGuard<CircularQueue<i16>>) 
            where T: cpal::Sample {
                for sample in samples.iter() {
                    q.push(sample.to_i16());
                }
        }

        match buffer.lock() {
            Ok(mut guard) => insert(input, &mut guard),
            Err(_) => eprintln!("(audioio) - Failed to aquire lock for writing audio data")
        }

    }

fn get_recording_device(_: &RecordingConfig) -> Result<cpal::Device, FridayError> {
    //for host in cpal::available_hosts().iter() {
        //println!("Found Host {}", host.name());
    //}
    //for device in cpal::default_host().input_devices().unwrap() {
        //println!("Found {}", device.name().unwrap());
    //}

    //for device in cpal::default_host().devices().unwrap() {
        //println!("Found device {}", device.name().unwrap());
    //}
    // TODO: Make a smart choice of device here
    // For some platforms the default device is not a good choice
    // E.g raspberry PI
    // The current work-around is that I manually set the default device on the pi
    // to make this code work - but would be better if this code could
    // recognize what device has recording capabilities and then use it


    return match cpal::default_host().default_input_device() {
        Some(device) => Ok(device),
        None => frierr!("Could not find any default input device for recording")
    };

}

impl Recorder for CPALIStream {
    fn read(&self) -> Option<Vec<i16>> {
        return match self.buffer.lock() {
            Ok(guard) => {
                let mut data: Vec<i16> = Vec::with_capacity(self.config.model_frame_size);
                data.extend(guard.asc_iter());
                data.resize(self.config.model_frame_size, 0);
                return Some(data);
            }
            Err(_) => {
                eprint!("Failed to aquire lock for reading audio data");
                None
            }
        }
    }

    fn record(conf: &RecordingConfig) -> Result<Box<CPALIStream>, FridayError> {
        return get_recording_device(conf)
            .map_or_else(
                |err| err.push("Could not setup any recording device...").into(),
                |device| {
                    println!("Using device {}", device.name().unwrap());

                    let config = cpal::StreamConfig {
                        channels: 1,
                        sample_rate: cpal::SampleRate{ 0: conf.sample_rate },
                        buffer_size: cpal::BufferSize::Default,
                    };

                    let write_buffer = Arc::new(
                        Mutex::new(
                            CircularQueue::with_capacity(conf.model_frame_size)));

                    let read_buffer = write_buffer.clone();

                    return device.build_input_stream(
                        &config.into(),
                        move |data, _: &_| write_to_buffer::<i16>(data, &write_buffer),
                        |err| println!("Recording error - {}", err)
                    ).map_or_else(
                    |err| frierr!("Failed to create input stream: {}", err),
                    |stream| {
                        stream.play()
                            .map_or_else(
                                |err| frierr!("Recording Failed {}", err),
                                |_| {
                                    Ok(Box::new(CPALIStream{
                                        config: conf.clone(),
                                        _stream: stream,
                                        buffer: read_buffer}))
                                })

                    });
                });
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::path::Path;
    use wav;
    #[test]
    fn cpal_some_printing() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = CPALIStream::record(&r).unwrap();


        std::thread::sleep(std::time::Duration::from_secs(1));
        match istream.read() {
            Some(v) => println!("{:?}", v[0..1000].iter()),
            _ => println!("Failed to read")
        }

        std::thread::sleep(std::time::Duration::from_secs(2));
        println!();

        match istream.read() {
            Some(v) => println!("{:?}", v[0..1000].iter()),
            _ => println!("Failed to read")
        }



    }

    #[test]
    fn normal_workload() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = CPALIStream::record(&r).unwrap();


        for _ in 0..50 {
            std::thread::sleep(std::time::Duration::from_millis(250));
            match istream.read() {
                Some(_) => println!("Read Ok!"),
                _ => println!("Failed to read")
            }

        }

    }

    #[test]
    fn record_audio_files() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = CPALIStream::record(&r).unwrap();


        for index in 0..8 {
            std::thread::sleep(std::time::Duration::from_millis(2000));
            match istream.read() {
                Some(data) => {
                    println!("Read Ok!");
                    let out = File::create(
                        Path::new(&format!("test-{}.wav", index)));

                    match out {
                        Ok(mut fw) => {
                            let header = wav::Header::new(1, 1, r.sample_rate, 16);
                            match wav::write(header, wav::BitDepth::Sixteen(data), &mut fw) {
                                Ok(_) => println!("Successfully wrote to wav file!"),
                                Err(e) => println!("Failed to write to wav file - Reason: {}", e)
                            }

                        },
                        Err(e) => println!("Failed to create out file - Reason: {}", e)
                    }




                },
                _ => println!("Failed to read")
            }

        }

    }
}
