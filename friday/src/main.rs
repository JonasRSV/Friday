use ctrlc;
use vendor_io;
use philips_hue;
use vendor_io::DispatchResponse;
use audio_io;
use audio_io::recorder::Recorder;
use inference;
use tensorflow_models;
use speaker_detection;
use speaker_detection::SpeakDetector;
use inference::Model;
use vendor_io::Vendor;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;


fn main() {
    let vendors: Vec<Box<dyn vendor_io::Vendor>> = vec![
        Box::new(philips_hue::Hue::new().expect("Failed to create Philips Hue Vendor")),
        Box::new(vendor_io::DummyVendor::new()),
    ];

    let mut model = tensorflow_models::discriminative::Discriminative::new()
        .expect("Failed to load model");

    let mut speak = speaker_detection::EnergyBasedDetector::new(
        /*threshold=*/400.0
    );

    let config = audio_io::RecordingConfig {
        sample_rate: 8000,
        model_frame_size: model.expected_frame_size()
    };


    let istream = audio_io::friday_cpal::CPALIStream::record(
        &config).expect("Failed to start audio recording");


    serve_friday(&mut speak, &mut model, &vendors, istream);

    println!("Exiting..");
}


fn serve_friday<M, S, V, R>(speak: &mut S, model: &mut M, vendors: &Vec<Box<V>>, istream: Box<R>) 
    where M: Model,
          S: SpeakDetector,
          V: Vendor + ?Sized,
          R: Recorder {

              // Create interrupt handler
              let running = Arc::new(AtomicBool::new(true));
              let r = running.clone();
              ctrlc::set_handler(move || {
                  r.store(false, Ordering::SeqCst);
              }).expect("Error setting Ctrl-C handler");

              // Run forever-loop
              println!("Listening..");
              while running.load(Ordering::SeqCst) {
                  std::thread::sleep(std::time::Duration::from_millis(250));
                  match istream.read() {
                      Some(audio) => {
                          if speak.detect(&audio) {
                              match model.predict(&audio) {
                                  inference::Prediction::Result{
                                      class,
                                      index: _
                                  } => {
                                      for vendor in vendors.iter() {
                                          match vendor.dispatch(&class) {
                                              DispatchResponse::Success => (),
                                              DispatchResponse::NoMatch => (),
                                              DispatchResponse::Err{err} => eprintln!(
                                                  "Error occured during dispatch {:?}", err)
                                          }
                                      }

                                      // Sleep to clear the replay buffer
                                      // TODO: maybe just empty the buffer instead of sleeping?
                                      std::thread::sleep(std::time::Duration::from_millis(2000));
                                  },
                                      inference::Prediction::Silence => (),
                                      inference::Prediction::Inconclusive => ()
                              };
                          }
                      },
                      None => eprintln!("(main) Failed to read audio")
                  }
              }
          }
