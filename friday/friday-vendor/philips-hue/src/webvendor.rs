use crate::serializeable_lights;
use crate::core::{
    HueCommandConfig, 
    HueLogin};

use crate::vendor::Hue;
use friday_error::FridayError;
use friday_error::propagate;
use friday_error::frierr;
use friday_web;

use huelib;

use std::sync::{Arc, Mutex, RwLock, MutexGuard};
use std::net::IpAddr;

use serde_json;


pub struct WebHue {
    endpoints: Vec<friday_web::endpoint::Endpoint>,

    // Need to have this hidden behind locks
    // because they are also used by the Vendor
    bridge: Arc<Mutex<Option<huelib::Bridge>>>,
    commands: Arc<RwLock<HueCommandConfig>>,
}

impl WebHue {
    pub fn new(h: &Hue) -> WebHue {
        WebHue {
            endpoints: vec![
                // Returns philips hue json response of all lights
                friday_web::endpoint::Endpoint{ 
                    name: "lights".to_owned(),
                    methods: vec![friday_web::core::Method::Get],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/lights")
                },
                // Returns 200 if a login is successful
                friday_web::endpoint::Endpoint{ 
                    name: "login".to_owned(),
                    methods: vec![friday_web::core::Method::Get],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/login")
                },
                // Getting / Putting Commands
                // Getting commands will return the command map
                // Putting commands will update the command-map with the content of
                // PUT if it is a valid command-map
                friday_web::endpoint::Endpoint{ 
                    name: "commands".to_owned(),
                    methods: vec![friday_web::core::Method::Get, friday_web::core::Method::Put],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/commands")
                }
            ],
            bridge: h.bridge.clone(),
            commands: h.commands.clone()
        }
    }

    fn create_lights_response_with_bridge(b: &huelib::Bridge) 
        -> Result<friday_web::core::Response, FridayError> {
            return match b.get_all_lights() {
                Err(err) => frierr!("Error occurred while querying for all lights: {}", err),
                Ok(lights) => serde_json::to_string(
                    &lights
                    .into_iter()
                    // Huelib Lights does not support serialization so we wrap them in a
                    // serializeable type
                    .map(serializeable_lights::Light::from) 
                    .collect::<Vec<serializeable_lights::Light>>()
                ).map_or_else(
                |err| frierr!("Failed to serialize lights to json response - Reason {}", err),
                |content| Ok(friday_web::core::Response::JSON {status: 200, content }))

            }

    }

    /// Returns available lights - Same as querying hue /lights api
    /// See the response from the Hue developer docs.
    fn lights(&self) -> Result<friday_web::core::Response, FridayError> {
        // Start with checking that we're logged in 
        match self.bridge.lock() {
            Ok(maybe_bridge) => match *maybe_bridge {
                // Not logged in 
                None => Ok(friday_web::core::Response::TEXT {
                    status: 405, 
                    content: "Please login first".to_owned()}),
                    // We're logged in! 
                    Some(ref bridge) => WebHue::create_lights_response_with_bridge(bridge)
            },
            Err(err) => frierr!("Failed to aquire lock to check for login - Reason: {}", err)
        }
    }

    fn create_bridge_from_login(
        maybe_bridge: &mut MutexGuard<Option<huelib::Bridge>>, 
        login: &HueLogin) -> Result<friday_web::core::Response, FridayError> {
        // First we dereference the mutex guard reference then we dereference the mutex guard
        // to set the value - this is why we have **

        // Now we are logged in and hopefully bridge should be accessible to the vendor
        // as well.
        **maybe_bridge = Some( huelib::Bridge::new(
                IpAddr::V4(login.ip.parse().unwrap()), 
                login.user.clone())
        );

        Ok(friday_web::core::Response::Empty { status: 200})

    }


    /// Checks for existing login or creates login for the friday bridge and stores login.
    /// After getting a login this also create a HueBridge instance that is accessible from
    /// the main thread and also the Web Threads - this Bridge can be used to control and get
    /// information about hue gadgets.
    fn login(&mut self) -> Result<friday_web::core::Response, FridayError> {
        // Start with checking if we're logged in
        match self.bridge.lock() {
            Ok(mut maybe_bridge) => match *maybe_bridge {
                // We're already logged in
                Some(_) => Ok(friday_web::core::Response::Empty { status: 200}), 
                // Not logged in 
                None => 
                    match Hue::get_hue_login() {
                        Ok(login) => WebHue::create_bridge_from_login(&mut maybe_bridge, &login),
                        Err(login_from_file_err) => 
                            match Hue::create_hue_login() {
                                Ok(login) => WebHue::create_bridge_from_login(&mut maybe_bridge, &login),
                                Err(create_login_err) => frierr!(
                                    "login failed - tryin to read existing login gave {:?}\
                                     Trying to create new login gave {:?}", login_from_file_err,
                                     create_login_err)
                            }
                    }

            },
            Err(err) => frierr!("Failed to aquire lock to check for login - Reason: {}", err)
        }

    }
}


impl friday_web::vendor::Vendor for WebHue{
    fn name(&self) -> String { return "friday-vendor/philips-hue".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> 
        Result<friday_web::core::Response, FridayError> {
            match friday_web::get_name(r, &self.endpoints) {
                Err(err) => propagate!("Failed to get 'Hue' endpoint for {}", r.url())(err),
                Ok(name) => match name.as_str() {
                    "lights" => self.lights(),
                    "login" => self.login(),
                    "commands" => match r.method() {
                        friday_web::core::Method::Put => todo!(),
                        friday_web::core::Method::Get => todo!(),
                        m => frierr!("Only Put or Get is accepted for 'WebHue' commands endpoint\
                            I received: {:?}", m)

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

    #[test]
    fn create_login_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_WEB_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handles = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/philips-hue/login").call();

        // Means login success! :)
        assert_eq!(resp.status(), 200);

        server.running.swap(false, std::sync::atomic::Ordering::Relaxed);
        for handle in handles {
            handle.join().expect("Failed to join thread");
        }

    }

    #[test]
    fn query_lights() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_WEB_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handles = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/philips-hue/lights").call();

        // Getting lights went fine!
        assert_eq!(resp.status(), 200);

        let lights : Vec<huelib::resource::Light> = 
            resp.into_json_deserialize::<Vec<serializeable_lights::Light>>()
            .expect("Failed to parse json response").into_iter().map(huelib::resource::Light::from).collect();
        println!("Lights response: {:?}", lights);


        server.running.swap(false, std::sync::atomic::Ordering::Relaxed);
        for handle in handles {
            handle.join().expect("Failed to join thread");
        }
    }
}
