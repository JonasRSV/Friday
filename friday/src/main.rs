use ctrlc;
use philips_hue;
use friday_vendor;
use friday_vendor::DispatchResponse;
use friday_vendor::Vendor;
use friday_audio;
use friday_audio::recorder::Recorder;
use friday_vad;
use friday_vad::SpeakDetector;
use friday_inference;
use friday_inference::Model;
use tensorflow_models;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use friday_web::server::Server;


fn main() {
    let vendors: Vec<Box<dyn friday_vendor::Vendor>> = vec![
        Box::new(philips_hue::Hue::new().expect("Failed to create Philips Hue Vendor")),
        Box::new(friday_vendor::DummyVendor::new()),
    ];


    let mut model = tensorflow_models::discriminative::Discriminative::new()
        .expect("Failed to load model");

    let mut vad = friday_vad::EnergyBasedDetector::new(
        /*threshold=*/350.0
    );

    let config = friday_audio::RecordingConfig {
        sample_rate: 8000,
        model_frame_size: model.expected_frame_size()
    };


    let istream = friday_audio::friday_cpal::CPALIStream::record(
        &config).expect("Failed to start audio recording");


    let mut server = Server::new().expect("Failed to create webserver");

    // TODO: Here we register web-vendors for the modules
    server.register(
        vec![]
    ).expect("Failed to register vendors");

    // Starts the server - this is non-blocking
    // Currently this starts two threads 
    let handles = server.listen("0.0.0.0:8000").expect("Failed to start webserver");


    serve_friday(&mut vad, &mut model, &vendors, istream);

    println!("Shutting Down Webserver.. Might take a few seconds");
    // Tell webserver theads to stop serving
    server.running.swap(false, Ordering::Relaxed);
    for thread in handles {
        // Join threads gracefully.. hopefully :)
        thread.join().expect("failed to join webserver thread");
    }


    println!("Exiting..");
}


fn serve_friday<M, S, V, R>(vad: &mut S, model: &mut M, vendors: &Vec<Box<V>>, istream: Box<R>) 
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
                          if vad.detect(&audio) {
                              match model.predict(&audio) {
                                  friday_inference::Prediction::Result{
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
                                      friday_inference::Prediction::Silence => (),
                                      friday_inference::Prediction::Inconclusive => ()
                              };
                          }
                      },
                      None => eprintln!("(main) Failed to read audio")
                  }
              }
          }
