mod tests;
mod serving;

use friday_vendor;
use vendor_scripts;
use friday_audio;
use friday_vad;
use friday_discovery;
use friday_logging;
use friday_signal;

use friday_inference;
use friday_inference::Model;
use tensorflow_models;

use friday_web::server::Server;


use std::sync::{Arc, Mutex};
use std::cell::RefCell;
use std::rc::Rc;


fn main() {

    // Tensorflow model that identifies keywords present in speech
    let mut model = tensorflow_models::ddl::interface::DDL::new()
        .expect("Failed to load model");

    let recording_config = friday_audio::RecordingConfig::new(
        16000, 
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
                friday_audio::web::record::api::WebRecord::new(
                    istream.clone()).expect("Failed to create WebRecord")
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

    let mut composer = friday_signal::Composer::new().expect("Failed to construct signal composer");

    composer.register_devices(
        vec![
            //Rc::new(RefCell::new(friday_signal::mock::MockDevice{}))
            
        ]
    );

    // Serve friday using the main thread
    serving::serve_friday(&mut vad, &mut model, &vendors, istream, &mut composer);

    friday_logging::info!("Shutting Down Webserver.. Might take a few seconds");
    web_handle.stop();
    friday_logging::info!("Shutting Down Discovery Server.. Might take a few seconds");
    discovery_handle.stop();


    friday_logging::info!("All Done - Bye!");
}


