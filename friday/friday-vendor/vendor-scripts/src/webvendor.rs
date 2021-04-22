use crate::vendor;
use friday_error::{frierr, propagate, FridayError};
use friday_web;
use friday_storage;
use friday_logging;

use std::sync::{Arc, RwLock};

use std::collections::HashMap;


pub struct WebScripts {
    endpoints: Vec<friday_web::endpoint::Endpoint>,

    // Need to have this hidden behind locks
    // because they are also used by the Vendor
    config: Arc<RwLock<vendor::Config>>,
    files: friday_storage::files::Files
}

impl WebScripts {
    pub fn new(h: &vendor::Scripts) -> WebScripts {
        WebScripts {
            endpoints: vec![
                // Returns philips hue json response of all lights
                friday_web::endpoint::Endpoint{ 
                    name: "bound".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get,
                        friday_web::core::Method::Put,
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/scripts/bound")
                },
                friday_web::endpoint::Endpoint{ 
                    name: "all".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get,
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/scripts/all")
                },
            ],
            config: h.config.clone(),
            files: h.files.clone()
        }
    }

    /// This responds with all scripts on the assistant
    fn get_all_scripts(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.files.list_files_under("") {
            Ok(files) => friday_web::json!(200, &files),
            Err(err) => frierr!("Failed to list all Scripts - Reason: {:?}", err)
        }
    }

    /// This responds with the scripts bound on the assistant
    fn get_bound_scripts(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.config.read() {
            Ok(config) => friday_web::json!(200, &config.scripts),
            Err(err) => frierr!("Failed to aquire config lock - Reason: {}", err)
        }
    }

    /// This updates the scripts on the assistant and stores them to disk
    fn set_bound_scripts(&self, scripts: HashMap<String, Vec<String>>) 
        -> Result<friday_web::core::Response, FridayError> {
            match self.config.write() {
                Ok(mut config) => {
                    // Updates the scripts config shared with the vendor that dispatches scripts 
                    (*config).scripts = scripts.clone();

                    // Here we store the  scripts config to disk so that next time friday is launched
                    // it has the new scripts
                    match friday_storage::config::write_config(&*config, "scripts.json") {
                        // Successfully stored scripts - all is well in the world! 
                        Ok(_) => friday_web::ok!("All good!"),

                        // What to do here is not clear.. we have successfully updated this session
                        // with the new scripts - but we have failed to store them - so the next
                        // time friday is restarted they will be forgotten. 
                        //
                        // Potentially we could try to store to disk before updating - but then at the
                        // risk of not updating for this session due to disk error...
                        // TODO: Think about what the best UX for this is
                        Err(err) => {
                            friday_logging::warning!("Failed to store scripts to disk - Reason: {:?}", 
                                err);

                            friday_web::ok!("Updated for this session - But failed to store on disk")
                        }
                    }


                }
                Err(err) => frierr!("Failed to aquire 'Scripts' lock - Reason: {}", err)
            }
    }
}


impl friday_web::vendor::Vendor for WebScripts {
    fn name(&self) -> String { return "friday-vendor/scripts".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> 
        Result<friday_web::core::Response, FridayError> {
            match friday_web::get_name(r, &self.endpoints) {
                Err(err) => propagate!("Failed to get 'Scripts' endpoint for {}", r.url())(err),
                Ok(name) => match name.as_str() {

                    "bound" => match r.method() {
                        // This returns the commands as a JSON file
                        friday_web::core::Method::Get => self.get_bound_scripts(),     // This gets the commands
                        // This updates the commands and stores updates to disk
                        friday_web::core::Method::Put => friday_web::request_json(
                            r,
                            &|scripts| self.set_bound_scripts(scripts)),
                        m => friday_web::not_acceptable!("Only Put or Get is accepted for 'WebScripts'\
                            endpoint I received: {:?}", m)

                    },
                    "all" => self.get_all_scripts(),

                    _ => frierr!("Unknown endpoint name {}", name)
                }
            }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use ureq;
    use std::sync::Mutex;


    #[test]
    fn get_bound_scripts_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let scripts_vendor = vendor::Scripts::new().expect("Failed to create scripts vendor");
        let web_scripts_vendor = WebScripts::new(&scripts_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_scripts_vendor))
        ]).expect("Failed to register scripts web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/scripts/bound").call();

        // Getting scripts went fine!
        assert_eq!(resp.status(), 200);

        let scripts : HashMap<String, Vec<String>> = 
            resp.into_json_deserialize::<HashMap<String, Vec<String>>>()
            .expect("Failed to parse json response");

        friday_logging::info!("scripts response: {:?}", scripts);

        handle.stop();
    }

    #[test]
    fn get_all_scripts_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let scripts_vendor = vendor::Scripts::new().expect("Failed to create scripts vendor");
        let web_scripts_vendor = WebScripts::new(&scripts_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_scripts_vendor))
        ]).expect("Failed to register scripts web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/scripts/all").call();

        // Getting scripts went fine!
        assert_eq!(resp.status(), 200);

        let scripts : Vec<String> = 
            resp.into_json_deserialize::<Vec<String>>()
            .expect("Failed to parse json response");

        friday_logging::info!("all scripts response: {:?}", scripts);

        handle.stop();
    }

    #[test]
    fn set_bound_scripts_via_web() {
            env::set_var("FRIDAY_CONFIG", "./test-resources");
            env::set_var("FRIDAY_GUI", ".");

            let scripts_vendor = vendor::Scripts::new().expect("Failed to create scripts vendor");
            let web_scripts_vendor = WebScripts::new(&scripts_vendor);

            let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
            server.register(vec![
            Arc::new(Mutex::new(web_scripts_vendor))
            ]).expect("Failed to register scripts web vendor");

            let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

            std::thread::sleep(std::time::Duration::from_millis(1000));

            let update: HashMap<String, Vec<String>> = [
                ("hi".to_owned(), vec!["cookies.sh".to_owned(), "woo.sh".to_owned()])
            ].iter().cloned().collect();




            let resp = ureq::put("http://0.0.0.0:8000/friday-vendor/scripts/bound")
            .send_json(serde_json::to_value(update).expect("Failed to serialize state"));

            // Setting scripts went fine!
            assert_eq!(resp.status(), 200);

            handle.stop();
    }

}
