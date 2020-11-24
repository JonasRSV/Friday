use ctrlc;
use action_io;
use audio_io;
use inference;
use tensorflow_models;
use inference::Model;
use action_io::Vendor;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;



fn main() {
    let vendors: Vec<Box<dyn action_io::Vendor>> = vec![
        Box::new(action_io::DummyVendor::new()),
        Box::new(action_io::DummyVendor::new()),
    ];

    let mut model = tensorflow_models::discriminative::Discriminative::new();

    let config = audio_io::RecordingConfig {
        sample_rate: 8000,
        buffer_size: 2000,
        model_frame_size: model.expected_frame_size()
    };

    let istream = audio_io::record(&config);

    serve_friday(&mut model, &vendors, &istream);

    println!("Exiting..");

    drop(istream);
    drop(config);
    drop(model);
    drop(vendors);
}


fn serve_friday<M, V>(model: &mut M, vendors: &Vec<Box<V>>, istream: &audio_io::IStream) 
    where M: Model,
          V: Vendor + ?Sized {

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
                          let prediction = model.predict(&audio);

                          for vendor in vendors.iter() {
                              match vendor.dispatch(&prediction.class) {
                                  Ok(_) => (),
                                  Err(e) => eprintln!("Failed to dispatch {}", e)
                              }
                          }

                      },
                      None => eprintln!("(main) Failed to read audio")

                  }

              }

}
