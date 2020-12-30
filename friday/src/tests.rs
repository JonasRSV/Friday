

#[cfg(test)]
mod tests {
    use friday_logging;

    fn infinite_interruptable_loop() {
              let running = Arc::new(AtomicBool::new(true));
              let r = running.clone();
              ctrlc::set_handler(move || {
                  r.store(false, Ordering::SeqCst);
              }).expect("Error setting Ctrl-C handler");

              // Run forever-loop
              println!("Listening..");
              while running.load(Ordering::SeqCst) {
                  std::thread::sleep(std::time::Duration::from_millis(500));
              }

    }

    use crate::*;
    use std::env;

    // This 'test' starts the webserver running on friday - might be nice to have this running
    // when developing UI's.. if you don't want to run the rest of friday also.
    #[test]
    fn webserver() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        // Path to UI you want to run this with
        env::set_var("FRIDAY_GUI", ".");

        let mut server = Server::new().expect("Failed to create webserver");

        let hue_vendor = philips_hue::vendor::Hue::new().expect("Failed to create Philips Hue Vendor");
        let model = tensorflow_models::discriminative::Discriminative::new()
            .expect("Failed to load model");
        let discovery = friday_discovery::discovery::Discovery::new(8000)
            .expect("Failed to create discovery");

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
                    philips_hue::webvendor::WebHue::new(&hue_vendor)
                )
            ),

            Arc::new(
                Mutex::new(
                    friday_discovery::webvendor::WebDiscovery::new(&discovery)
                )
            )

            ]
        ).expect("Failed to register vendors");


        // Non-blocking webserver serving the web vendors Currently this starts two threads 
        let handle = server.listen("0.0.0.0:8000").expect("Failed to start webserver");

        infinite_interruptable_loop();

        friday_logging::info!("Shutting Down Webserver.. Might take a few seconds");
        // Tell webserver theads to stop serving
        handle.stop();


        friday_logging::info!("Exiting..");
    }
}
