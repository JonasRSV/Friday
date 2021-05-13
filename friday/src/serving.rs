use friday_vendor;
use friday_vendor::DispatchResponse;
use friday_vendor::Vendor;
use friday_signal;


use friday_audio;
use friday_audio::recorder::Recorder;

use friday_vad;
use friday_vad::core::{SpeakDetector, VADResponse};

use friday_inference;
use friday_inference::Model;


use friday_logging;

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

use ctrlc;


fn dispatch<V>(vendors: &Vec<Box<V>>, class: String) where V: Vendor + ?Sized {
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
}

pub fn serve_friday<M, S, V, R>(
    vad: &mut S, 
    model: &mut M, 
    vendors: &Vec<Box<V>>, 
    shared_istream: Arc<Mutex<R>>,
    composer: &mut friday_signal::Composer) 
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

              friday_logging::info!("Purging some audio... (takes 2 seconds)");
              std::thread::sleep(std::time::Duration::from_millis(2000));

              // State to keep track if previous audio was inferred on
              // If we go from inference to silence we reset any state the model might have.
              let mut previous_was_inference = false;

              // Run forever-loop
              friday_logging::info!("Listening..");

              // Friday is listening
              composer.send(&friday_signal::core::Signal::StartListening);
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
                                  match vad.detect(&audio) {
                                      VADResponse::Voice => {
                                          // VAD got voice so we will run inference
                                          // as long as this is true the model gets to keep its
                                          // state.
                                          previous_was_inference = true;

                                          // Friday starts inferring
                                          composer.send(&friday_signal::core::Signal::StartInferring);

                                          match model.predict(&audio) {
                                              Ok(prediction) => match prediction {
                                                  friday_inference::Prediction::Result{
                                                      class,
                                                  } => {
                                                      friday_logging::info!("Dispatching {}", class);

                                                      // Friday starts dispatching
                                                      composer.send(&friday_signal::core::Signal::StartDispatching);

                                                      //Sleep to clear the replay buffer
                                                      //std::thread::sleep(std::time::Duration::from_millis(2000));


                                                      // Clear buffer of any trace of the signal
                                                      // that trigged this command
                                                      match istream.clear() {
                                                          Err(err) => {
                                                              friday_logging::fatal!(
                                                                  "Failed to clear audio buffer, Reason: {:?} \
                                                              exiting..", err);
                                                              break;
                                                          },
                                                          Ok(()) => ()
                                                      };

                                                      // Dispatch the command
                                                      dispatch(vendors, class);

                                                      // Friday stops dispatching
                                                      composer.send(&friday_signal::core::Signal::StopDispatching);
                                                  },
                                                  friday_inference::Prediction::Silence => (),
                                                  friday_inference::Prediction::Inconclusive => ()
                                              },
                                              Err(err) => friday_logging::error!(
                                                  "Failed to do inference - Reason: {:?}", err)
                                          }

                                      },
                                      VADResponse::Silence => {
                                          if previous_was_inference {
                                              composer.send(&friday_signal::core::Signal::StopInferring);

                                              match model.reset() {
                                                  Ok(()) => friday_logging::debug!("Model was reset"),
                                                  Err(err) => {
                                                      friday_logging::fatal!(
                                                          "Failed to reset model, Reason: {:?} \
                                                      exiting..", err);
                                                      break;



}                                              }
                                          }

                                          previous_was_inference = false;
                                      }
                                  }
                              },
                              None => friday_logging::error!("(main) Failed to read audio")
                          }
                  }
              }
          }
