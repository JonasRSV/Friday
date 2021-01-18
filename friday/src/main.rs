mod tests;

use friday_vendor;
use friday_vendor::DispatchResponse;
use friday_vendor::Vendor;

use vendor_philips_hue;

use friday_audio;
use friday_audio::recorder::Recorder;

use friday_vad;
use friday_vad::core::SpeakDetector;

use friday_inference;
use friday_inference::Model;
use tensorflow_models;

use friday_web::server::Server;

use friday_discovery;

use friday_logging;

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

use ctrlc;


fn main() {

    // For webserver & discovery
    let port: u16 = 8000;

    // Webserver that serves the GUI and also all of fridays endpoints
    let mut server = Server::new().expect("Failed to create webserver");
    let discovery = friday_discovery::discovery::Discovery::new(port)
        .expect("Failed to create discovery");

    let hue_vendor = vendor_philips_hue::vendor::Hue::new().expect("Failed to create Philips Hue Vendor");

    // Tensorflow model that identifies the keyword present in speech
    let mut model = tensorflow_models::discriminative::Discriminative::new()
        .expect("Failed to load model");

    server.register(
        vec![
        // Webserver for discriminiative model to serve its info
        Arc::new(
            Mutex::new(
                tensorflow_models::discriminative::WebDiscriminative::new(&model)
            )
        ),

        // Webserver for philips_hue vendor to control lights and light actions 
        Arc::new(
            Mutex::new(
                vendor_philips_hue::webvendor::WebHue::new(&hue_vendor)
            )
        ),

        Arc::new(
            Mutex::new(
                friday_discovery::webvendor::WebDiscovery::new(&discovery)
            )
        )

            ]
            ).expect("Failed to register vendors");


    let recording_config = friday_audio::RecordingConfig {
        sample_rate: 8000,
        model_frame_size: model.expected_frame_size()
    };

    // Input audio stream 
    let istream = friday_audio::friday_cpal::CPALIStream::record(
        &recording_config).expect("Failed to start audio recording");


    let vendors: Vec<Box<dyn friday_vendor::Vendor>> = vec![
        Box::new(hue_vendor)
    ];


    // Non-blocking webserver serving the web vendors Currently this starts two threads 
    let web_handle = server.listen(format!("0.0.0.0:{}", port))
        .expect("Failed to start webserver");
    // Non-blocking discovery server (Tries to make it easy to discover the assistant)
    let discovery_handle = discovery.make_discoverable();

    // Cheap voice activity detection - if this one triggers we then trigger
    // the tensorflow model
    let mut vad = friday_vad::vad_energy::EnergyBasedDetector::new()
        .expect("Failed to create VAD - EnergyBasedDetector");

    // Serve friday using the main thread
    serve_friday(&mut vad, &mut model, &vendors, istream);

    friday_logging::info!("Shutting Down Webserver.. Might take a few seconds");
    web_handle.stop();
    friday_logging::info!("Shutting Down Discovery Server.. Might take a few seconds");
    discovery_handle.stop();


    friday_logging::info!("All Done - Bye!");
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
              friday_logging::info!("Listening..");
              while running.load(Ordering::SeqCst) {
                  std::thread::sleep(std::time::Duration::from_millis(250));
                  match istream.read() {
                      Some(audio) => {
                          if vad.detect(&audio) {
                              match model.predict(&audio) {
                                  Ok(prediction) => match prediction {
                                      friday_inference::Prediction::Result{
                                          class,
                                          index: _
                                      } => {
                                          for vendor in vendors.iter() {
                                              match vendor.dispatch(&class) {
                                                  Ok(dispatch_response) => match dispatch_response {
                                                      DispatchResponse::Success => (),
                                                      DispatchResponse::NoMatch => ()
                                                  },
                                                  Err(err) => friday_logging::error!(
                                                      "Failed to dispatch {} - Reason: {:?}", 
                                                      vendor.name(),
                                                      err)
                                              }
                                          }

                                          // Sleep to clear the replay buffer
                                          // TODO: maybe just empty the buffer instead of sleeping?
                                          std::thread::sleep(std::time::Duration::from_millis(2000));

                                      },
                                          friday_inference::Prediction::Silence => (),
                                          friday_inference::Prediction::Inconclusive => ()
                                  },
                                  Err(err) => friday_logging::error!("Failed to do inference - Reason: {:?}", err)
                              };
                          }
                      },
                      None => friday_logging::error!("(main) Failed to read audio")
                  }
              }
          }
