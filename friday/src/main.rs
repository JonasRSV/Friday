mod tests;
mod web;

use friday_vendor;
use friday_vendor::DispatchResponse;
use friday_vendor::Vendor;

use vendor_scripts;

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

    // Tensorflow model that identifies keywords present in speech
    let mut model = tensorflow_models::ddl::interface::DDL::new()
        .expect("Failed to load model");

    let recording_config = friday_audio::RecordingConfig::new(
        8000, 
        model.expected_frame_size()).expect("Could not initialize 'RecordingConfig'");

    // Input audio stream, this is shared with the recording web-vendor
    let istream = 
        friday_audio::friday_cpal::CPALIStream::record(&recording_config)
        .expect("Failed to start audio recording");

    // For webserver & discovery
    let port: u16 = 8000;

    // Webserver that serves the GUI and also all of fridays endpoints
    let mut server = Server::new().expect("Failed to create webserver");

    // A separate thread for running discovery services
    let discovery = friday_discovery::discovery::Discovery::new(port)
        .expect("Failed to create discovery");

    // vendors
    let scripts_vendor = vendor_scripts::vendor::Scripts::new().expect("Failed to create 'Scripts' Vendor");

    server.register(
        vec![
        // Webserver for model to serve its info
        Arc::new(
            Mutex::new(
                tensorflow_models::ddl::interface::WebDDL::new(&model)
            )
        ),

        // Webserver for scripts vendor 
        Arc::new(
            Mutex::new(
                vendor_scripts::webvendor::WebScripts::new(&scripts_vendor)
            )
        ),

        // Webserver for discovery services: to set and get device name and pining remote server
        // for discoverfriday.se
        Arc::new(
            Mutex::new(
                friday_discovery::webvendor::WebDiscovery::new(&discovery)
            )
        ),

        // Webserver for recording and manipulating audio files on the assistant.
        // Is used to add keywords through the API.
        Arc::new(
            Mutex::new(
                web::record::api::WebRecord::new(istream.clone()).expect("Failed to create WebRecord")
            )
        )

            ]
            ).expect("Failed to register vendors");

    // Vendors that subscribe to keyword detections
    let vendors: Vec<Box<dyn friday_vendor::Vendor>> = vec![
        Box::new(scripts_vendor)
    ];


    // Non-blocking webserver serving the web vendors 
    let web_handle = server.listen(format!("0.0.0.0:{}", port))
        .expect("Failed to start webserver");
    // Non-blocking discovery server (Tries to make it easy to discover the assistant)
    let discovery_handle = discovery.make_discoverable();

    // Cheap voice activity detection - if this one triggers we then trigger
    // the tensorflow model
    let mut vad = friday_vad::vad_peaks::PeakBasedDetector::new()
        .expect("Failed to create VAD - PeakBasedDetector");

    // Serve friday using the main thread
    serve_friday(&mut vad, &mut model, &vendors, istream);

    friday_logging::info!("Shutting Down Webserver.. Might take a few seconds");
    web_handle.stop();
    friday_logging::info!("Shutting Down Discovery Server.. Might take a few seconds");
    discovery_handle.stop();


    friday_logging::info!("All Done - Bye!");
}


fn serve_friday<M, S, V, R>(
    vad: &mut S, 
    model: &mut M, 
    vendors: &Vec<Box<V>>, 
    shared_istream: Arc<Mutex<R>>) 
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
              friday_logging::info!("Purging some audio... (takes 2 seconds)");
              std::thread::sleep(std::time::Duration::from_millis(2000));

              // Run forever-loop
              friday_logging::info!("Listening..");
              while running.load(Ordering::SeqCst) {
                  std::thread::sleep(std::time::Duration::from_millis(250));
                  match shared_istream.lock() {
                      Err(err) => {
                          friday_logging::fatal!("Error occurred when aquiring istream mutex {:?}", err);

                          // Recovering from this is essentially restarting the assistant so we just
                          // break to exit
                          break;
                      }

                      Ok(istream) => 
                          match istream.read() {
                              Some(audio) => {
                                  if vad.detect(&audio) {
                                      match model.predict(&audio) {
                                          Ok(prediction) => match prediction {
                                              friday_inference::Prediction::Result{
                                                  class,
                                              } => {
                                                  friday_logging::info!("Dispatching {}", class);
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
                                          Err(err) => friday_logging::error!("Failed to do inference - Reason: {:?}", 
                                              err)
                                      };
                                  }
                              },
                              None => friday_logging::error!("(main) Failed to read audio")
                          }
                  }
              }
          }
