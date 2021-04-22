use cpal;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex, MutexGuard};
use circular_queue::CircularQueue;
use friday_error;
use friday_error::{frierr, propagate, FridayError};
use friday_logging;
use crate::recorder::Recorder;
use crate::RecordingConfig;

use std::thread;
use std::time;



fn write_to_buffer<T>(input: &[T], buffer: &Arc<Mutex<CircularQueue<i16>>>,
    loudness_contant: i16) 
    where T: cpal::Sample {
        fn insert<T>(samples: &[T], q: &mut MutexGuard<CircularQueue<i16>>, loudness: i16) 
            where T: cpal::Sample {
                for sample in samples.iter() {
                    let mut i16sample = sample.to_i16();

                    // To avoid overflowing issues
                    if i16sample == -32768 {
                        i16sample = -32767;
                    }

                    // To avoid overflowing issues
                    match i16sample.checked_mul(loudness) {
                        Some(v) => q.push(v),
                        None => q.push(i16sample)

                    };
                }
        }

        match buffer.lock() {
            Ok(mut guard) => insert(input, &mut guard, loudness_contant),
            Err(err) => {
                friday_logging::fatal!("(audioio) - Failed to aquire lock for writing audio data\
                - Reason: {}", err);

                // To not spam the living #!#! out of the audio device mutex if we get a poison
                // error
                thread::sleep(time::Duration::from_secs(1));
            }
        }

    }

fn get_recording_device(_: &RecordingConfig) -> Result<cpal::Device, FridayError> {
    //for host in cpal::available_hosts().iter() {
    //friday_logging::info!("Found Host {}", host.name());
    //}
    //for device in cpal::default_host().input_devices().unwrap() {
    //friday_logging::info!("Found {}", device.name().unwrap());
    //}

    //for device in cpal::default_host().devices().unwrap() {
    //friday_logging::info!("Found device {}", device.name().unwrap());
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

pub struct CPALIStream {
    config: RecordingConfig,
    _stream: cpal::Stream,
    buffer: Arc<Mutex<CircularQueue<i16>>>

}

// TODO(jonasrsv) Why does CPAL flag recording as not thread safe?
// If things break, this is likely a culprit
// It should be threadsafe though since we're using sync primitives for our audio buffer
unsafe impl Send for CPALIStream { }

impl CPALIStream {

    pub fn record(conf: &RecordingConfig) -> Result<Arc<Mutex<CPALIStream>>, FridayError> {
        return get_recording_device(conf)
            .map_or_else(
                propagate!("Could not setup any recording device..."),
                |device| {

                    friday_logging::info!("Using device {}", device.name().unwrap());

                    let config = cpal::StreamConfig {
                        channels: 1,
                        sample_rate: cpal::SampleRate{ 0: conf.sample_rate },
                        buffer_size: cpal::BufferSize::Default,
                    };

                    let write_buffer = Arc::new(
                        Mutex::new(
                            CircularQueue::with_capacity(conf.model_frame_size)));

                    let read_buffer = write_buffer.clone();
                    let loudness = conf.loudness.clone();

                    return device.build_input_stream(
                        &config.into(),
                        move |data, _: &_| write_to_buffer::<i16>(data, &write_buffer, loudness),
                        |err| {
                            friday_logging::fatal!("Recording error - {}", err);
                            // To not spam the living #!#! out of the audio device if an error
                            // occurs - e.g someone janks out the audio device from the
                            // computer
                            thread::sleep(time::Duration::from_secs(10));

                        }
                    ).map_or_else(
                    |err| frierr!("Failed to create input stream: {}", err),
                    |stream| {
                        stream.play()
                            .map_or_else(
                                |err| frierr!("Recording Failed {}", err),
                                |_| {
                                    Ok(Arc::new(Mutex::new(CPALIStream{
                                        config: conf.clone(),
                                        _stream: stream,
                                        buffer: read_buffer})))
                                })

                    });
                });
    }
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
            Err(err) => {
                friday_logging::fatal!("Failed to aquire lock for reading audio data -
                    Reason: {}", err);

                // To not spam the living #!#! out of the audio device mutex if we get a poison
                // error
                thread::sleep(time::Duration::from_secs(1));

                None
            }
        }
    }


    fn sample_rate(&self) -> u32 {
        self.config.sample_rate
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
            model_frame_size: 16000,
            loudness: 1
        };


        let istream = CPALIStream::record(&r).unwrap();


        std::thread::sleep(std::time::Duration::from_secs(1));
        match istream.clone().lock().unwrap().read() {
            Some(v) => friday_logging::info!("{:?}", v[0..1000].iter()),
            _ => friday_logging::info!("Failed to read")
        }

        std::thread::sleep(std::time::Duration::from_secs(2));

        match istream.clone().lock().unwrap().read() {
            Some(v) => friday_logging::info!("{:?}", v[0..1000].iter()),
            _ => friday_logging::info!("Failed to read")
        }



    }

    #[test]
    fn normal_workload() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000,
            loudness: 1
        };


        let istream = CPALIStream::record(&r).unwrap();


        for _ in 0..50 {
            std::thread::sleep(std::time::Duration::from_millis(250));
            match istream.lock().unwrap().read() {
                Some(_) => friday_logging::info!("Read Ok!"),
                _ => friday_logging::info!("Failed to read")
            }

        }

    }

    fn energy(audio: &Vec<i16>) -> f64 {
        let mut e = 0.0;
        for sample in audio.iter() {
            let f64sample = (sample.clone() as f64) / 32768.0;
            e += f64::sqrt(f64sample * f64sample);
        }
        return e / 16000.0;
    }

    #[test]
    fn record_audio_files() {
        let r = RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000,
            loudness: 1
        };


        let istream = CPALIStream::record(&r).unwrap();


        for index in 0..8 {
            std::thread::sleep(std::time::Duration::from_millis(2000));
            match istream.lock().unwrap().read() {
                Some(data) => {
                    friday_logging::info!("Read Ok!, energy {}", energy(&data));
                    let out = File::create(
                        Path::new(&format!("test-{}.wav", index)));

                    match out {
                        Ok(mut fw) => {
                            let header = wav::Header::new(1, 1, r.sample_rate, 16);
                            match wav::write(header, wav::BitDepth::Sixteen(data), &mut fw) {
                                Ok(_) => friday_logging::info!("Successfully wrote to wav file!"),
                                Err(e) => friday_logging::info!("Failed to write to wav file - Reason: {}", e)
                            }

                        },
                        Err(e) => friday_logging::info!("Failed to create out file - Reason: {}", e)
                    }




                },
                _ => friday_logging::info!("Failed to read")
            }

        }

    }
}
