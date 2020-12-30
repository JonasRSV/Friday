use crate::discovery::{Discovery, DiscoveryConfig};
use friday_error::{FridayError, frierr, propagate};
use friday_logging;
use friday_storage;
use std::sync::{RwLock, Arc};
use friday_web;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct NameMessage {
    name: String
}



/// A webvendor for the main discovery module
pub struct WebDiscovery{
    endpoints: Vec<friday_web::endpoint::Endpoint>,

    /// Name of the 'Friday'
    /// It is shared with the discovery module
    name: Arc<RwLock<String>>
}

impl WebDiscovery {
    pub fn new(d: &Discovery) -> WebDiscovery {
        WebDiscovery{
            endpoints: vec![
                friday_web::endpoint::Endpoint{ 
                    name: "name".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get, 
                        friday_web::core::Method::Put
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-discovery/name")
                },
            ],
            name: d.name.clone(),
        }
    }

    fn set_name(&self, message: NameMessage) -> Result<friday_web::core::Response, FridayError> {
        match self.name.write() {
            Ok(mut guard_name) => {
                *guard_name = message.name.clone();

                // We also store to disk for future sessions
                let maybe_err =friday_storage::config::write_config(&DiscoveryConfig {
                    name: message.name.clone()
                }, "discovery.json");

                if maybe_err.is_err() {
                    friday_logging::error!("Failed to write new device name to disk - Reason {:?}", 
                        maybe_err.unwrap_err());
                }


                friday_web::ok!("Updated name to {}", message.name)
            }
            Err(err) => frierr!("Unable to aquire lock for reading device name - Reason {}", err)
        }
    }

    fn get_name(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.name.read() {
            Ok(guard_name) => friday_web::json!(200, &NameMessage {
                name: guard_name.clone()
            }),

            Err(err) => frierr!("Unable to aquire lock for reading 'device' name - Reason: {}", err)
        }
    }
}

impl friday_web::vendor::Vendor for WebDiscovery {
    fn name(&self) -> String { return "friday-discovery/discovery".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> Result<friday_web::core::Response, FridayError> {
        return match friday_web::get_name(r, &self.endpoints) {
            Err(err) => propagate!("Failed to get 'Discovery' endpoint for {}", r.url())(err),
            Ok(name) =>  match name.as_str() {
                "name" => match r.method() {
                    friday_web::core::Method::Get => self.get_name(),     
                    friday_web::core::Method::Put => friday_web::request_json(r, 
                        &|message| self.set_name(message)),

                    m => friday_web::not_acceptable!(
                        "Only Put or Get is accepted for 'Discovery'\
                            name endpoint I received: {:?}", m)

                }
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
    use serde_json;
    use std::sync::Mutex;

    #[test]
    fn get_name() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let discovery = Discovery::new(8000).expect("Failed to create discovery");
        let web_discovery = WebDiscovery::new(&discovery);

        let mut server = friday_web::server::Server::new().expect("Failed to create friday webserver");
        server.register(vec![
            Arc::new(Mutex::new(web_discovery))
        ]).expect("Failed to register web discovery");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-discovery/name").call();

        assert_eq!(resp.status(), 200);

        println!("Got response {}", resp.into_string().unwrap());


        handle.stop();
    }

    #[test]
    fn set_name() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let discovery = Discovery::new(8000).expect("Failed to create discovery");
        let web_discovery = WebDiscovery::new(&discovery);

        let mut server = friday_web::server::Server::new().expect("Failed to create friday webserver");
        server.register(vec![
            Arc::new(Mutex::new(web_discovery))
        ]).expect("Failed to register web discovery");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::put("http://0.0.0.0:8000/friday-discovery/name").send_json(
            serde_json::json!({
                "name": "Hello"
            }));

        assert_eq!(resp.status(), 200);

        println!("Got response {}", resp.into_string().unwrap());


        handle.stop();
    }
}
