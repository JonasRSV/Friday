use cpal;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex, MutexGuard};
use circular_queue::CircularQueue;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;


#[derive(Clone)]
pub struct RecordingConfig {
    pub sample_rate: u32,
    pub buffer_size: u32,
    pub model_frame_size: usize
}

pub struct IStream {
    config: RecordingConfig,
    stream: cpal::Stream,
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
    return match cpal::default_host().default_input_device() {
        Some(device) => Ok(device),
        None => frierr!("Could not find any default input device for recording")
    };

}

pub fn record(r: &RecordingConfig) -> Result<Box<IStream>, FridayError> {
    return get_recording_device(r)
        .map_or_else(
            |err| err.push("Could not setup any recording device...").into(),
            |device| {
                let config = cpal::StreamConfig {
                    channels: 1,
                    sample_rate: cpal::SampleRate{ 0: r.sample_rate },
                    buffer_size: cpal::BufferSize::Fixed(r.buffer_size),
                };

                let write_buffer = Arc::new(
                    Mutex::new(
                        CircularQueue::with_capacity(r.model_frame_size)));

                let read_buffer = write_buffer.clone();

                return device.build_input_stream(
                    &config.into(),
                    move |data, _: &_| write_to_buffer::<i16>(data, &write_buffer),
                    |err| println!("Recording error - {}", err)
                ).map_or_else(
                |err| frierr!("Failed to create input stream {}", err),
                    |stream| {
                        stream.play()
                            .map_or_else(
                                |err| frierr!("Recording Failed {}", err),
                                |_| {
                                    Ok(Box::new(IStream{
                                        config: r.clone(),
                                        stream,
                                        buffer: read_buffer}))
                                })

                    });
            });
}

impl IStream {
    pub fn read(&self) -> Option<Vec<i16>> {
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
}

struct OStream;


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::path::Path;
    use wav;
    #[test]
    fn some_printing() {
        let r = RecordingConfig {
            sample_rate: 8000,
            buffer_size: 2000,
            model_frame_size: 16000
        };


        let istream = record(&r);


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



        drop(istream.stream);
    }

    #[test]
    fn normal_workload() {
        let r = RecordingConfig {
            sample_rate: 8000,
            buffer_size: 2000,
            model_frame_size: 16000
        };


        let istream = record(&r);


        for _ in 0..50 {
            std::thread::sleep(std::time::Duration::from_millis(250));
            match istream.read() {
                Some(_) => println!("Read Ok!"),
                _ => println!("Failed to read")
            }

        }

        drop(istream.stream);
    }

    #[test]
    fn record_audio_files() {
        let r = RecordingConfig {
            sample_rate: 8000,
            buffer_size: 2000,
            model_frame_size: 16000
        };


        let istream = record(&r);


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

        drop(istream.stream);
    }
}
