use crate::serializeable_lights;
use crate::core::{
    LightUpdate,
    HueCommandConfig, 
    HueLogin};

use crate::vendor;
use crate::vendor::Hue;
use friday_error::{frierr, propagate, FridayError};
use friday_web;
use friday_storage;
use friday_logging;

use huelib;

use std::sync::{Arc, Mutex, RwLock, MutexGuard};
use std::net::IpAddr;

use serde_json;
use std::collections::HashMap;


pub struct WebHue {
    endpoints: Vec<friday_web::endpoint::Endpoint>,

    // Need to have this hidden behind locks
    // because they are also used by the Vendor
    bridge: Arc<Mutex<Option<huelib::Bridge>>>,
    config: Arc<RwLock<HueCommandConfig>>,
}

impl WebHue {
    pub fn new(h: &Hue) -> WebHue {
        WebHue {
            endpoints: vec![
                // Returns philips hue json response of all lights
                friday_web::endpoint::Endpoint{ 
                    name: "lights".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get,
                        friday_web::core::Method::Put,
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/lights")
                },
                // Getting will return the light command map
                // Putting will update the light command map 
                friday_web::endpoint::Endpoint{ 
                    name: "lights/commands".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get, 
                        friday_web::core::Method::Put
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/lights/commands")
                },
                // Returns 200 if a login is successful
                friday_web::endpoint::Endpoint{ 
                    name: "login".to_owned(),
                    methods: vec![
                        friday_web::core::Method::Get,
                        friday_web::core::Method::Put
                    ],
                    path: friday_web::path::Path::safe_new(
                        "/friday-vendor/philips-hue/login")
                }
            ],
            bridge: h.bridge.clone(),
            config: h.config.clone()
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
    fn get_lights(&self) -> Result<friday_web::core::Response, FridayError> {
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

    /// Returns available lights - Same as querying hue /lights api
    /// See the response from the Hue developer docs.
    fn set_lights(&self, updates: Vec<LightUpdate>) -> Result<friday_web::core::Response, FridayError> {
        // Start with checking that we're logged in 
        match self.bridge.lock() {
            Ok(maybe_bridge) => match *maybe_bridge {
                // Not logged in 
                None => Ok(friday_web::core::Response::TEXT {
                    status: 405, 
                    content: "Please login first".to_owned()}),
                    // We're logged in! 
                    Some(ref bridge) => vendor::execute_light_updates(bridge, &updates).map(
                        |_| friday_web::core::Response::Empty {status: 200})
            },
            Err(err) => frierr!("Failed to aquire lock to check for login - Reason: {}", err)
        }
    }

    /// Checks if the bridge is created - if so we are logged in - if not we're not logged in
    fn is_logged_in(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.bridge.lock() {
            Ok(maybe_bridge) => match *maybe_bridge {
                // Not logged in - HTTP code I am a teapot - Why is there not a HTTP code for 'Not Ok' :(
                // TODO: If this is a horrible practise.. return a json with a bool instead
                None => Ok(friday_web::core::Response::Empty { status: 418 }),
                // We're logged in! 
                Some(_) => Ok(friday_web::core::Response::Empty { status: 200 })
            },
            Err(err) => frierr!("Failed to aquire lock to check for login - Reason: {}", err)
        }
    }

    /// This mutates the bridge pointer shared between web-vendors and 
    /// vendor to add an actual bridge.
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
                            // This also stores the login to disk
                            // Hopefully no other program is modifying the login for this program
                            // otherwise this can cause race a condition.. the race condition
                            // would not break the login for this session of the program
                            // but might cause a corrupted login file that causes issues the
                            // next time friday is launched.
                            //
                            // Now, no other programs should be messing with fridays login
                            // But if obscure errors occur it might be nice to keep this in mind.
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

    /// This responds with the command map used by the vendor
    fn get_lights_commands(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.config.read() {
            Ok(config) => serde_json::to_string(&config.lights).map_or_else(
                |err| frierr!("Failed to serialize config - Reason: {}", err),
                |content| Ok(friday_web::core::Response::JSON {status: 200, content})),
            Err(err) => frierr!("Failed to aquire config lock - Reason: {}", err)
        }
    }

    /// This sets the commands map and stores it to disk
    fn set_lights_commands(&self, new_lights_commands: HashMap<String, Vec<LightUpdate>>) 
        -> Result<friday_web::core::Response, FridayError> {
            match self.config.write() {
                Ok(mut config) => {
                    // Updates the command config shared with the vendor that dispatches hue commands
                    (*config).lights = new_lights_commands.clone();

                    // Here we store the command config to disk so that next time friday is launched
                    // it has the new commands
                    match friday_storage::config::write_config(&*config, "philips_hue.json") {
                        // Successfully stored commands - all is well in the world! 
                        Ok(_) => Ok(friday_web::core::Response::Empty {status: 200}),

                        // What to do here is not clear.. we have successfully updated this session
                        // with the new commands - but we have failed to store them - so the next
                        // time friday is restarted they will be forgotten. 
                        //
                        // Potentially we could try to store to disk before updating - but then at the
                        // risk of not updating for this session due to disk error...
                        // TODO: Think about what the best UX for this is
                        Err(err) => {
                            friday_logging::warning!("Failed to store new commands to disk - Reason: {:?}", 
                                err);

                            Ok(
                                friday_web::core::Response::TEXT {
                                    status: 200, 
                                    content: "Updated for this session - But failed to store on disk".to_owned()
                                }
                            )
                        }
                    }


                }
                Err(err) => frierr!("Failed to aquire commands lock - Reason: {}", err)
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
                    "lights" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Get => self.get_lights(), 
                        // This sets the state of the lights as provided in the JSON
                        friday_web::core::Method::Put => match r.data() {
                            Ok(data) => match data { 
                                // This JSON data is a string
                                // This just means that the content-type header was JSON
                                friday_web::core::Data::JSON { json } => 
                                    serde_json::from_str(&json).map_or_else(
                                        |err| frierr!(
                                            "Failed to deserialize JSON body - Reason : {}\n\
                                            BODY: {}", err, json),
                                            |updates| self.set_lights(updates)),
                                _ => friday_web::not_acceptable("Body must contain JSON data"),

                            },
                            Err(err) => propagate!("Unable to get data from request")(err)
                        }, 
                        m => friday_web::not_acceptable(
                            format!("Only Put or Get is accepted for 'WebHue'\
                                commands endpoint I received: {:?}", m))

                    }

                    "lights/commands" => match r.method() {
                        // This returns the commands as a JSON file
                        friday_web::core::Method::Get => self.get_lights_commands(),     // This gets the commands
                        // This updates the commands and stores updates to disk
                        friday_web::core::Method::Put => match r.data() {
                            Ok(data) => match data { 
                                // This JSON data is a string
                                // This just means that the content-type header was JSON
                                friday_web::core::Data::JSON { json } => 
                                    serde_json::from_str(&json).map_or_else(
                                        |err| frierr!(
                                            "Failed to deserialize JSON body - Reason : {}\n\
                                            BODY: {}", err, json),
                                            |commands| self.set_lights_commands(commands)),
                                _ => friday_web::not_acceptable("Body must contain JSON data"),

                            },
                            Err(err) => propagate!("Unable to get data from request")(err)
                        },     // This updates the commands

                        m => friday_web::not_acceptable(
                            format!("Only Put or Get is accepted for 'WebHue'\
                                commands endpoint I received: {:?}", m))

                    }

                    "login" => match r.method() { 
                        // This tries to login - blocks until success of fail after x seconds
                        friday_web::core::Method::Put => self.login(),        
                        // This gets login status - Returns 200 if success.. currently 418 if not
                        friday_web::core::Method::Get => self.is_logged_in(), 
                        m => friday_web::not_acceptable(
                            format!("Only Put or Get is accepted for 'WebHue'\
                                commands endpoint I received: {:?}", m))

                    },
                    _ => frierr!("Unknown endpoint name {}", name)
                }
            }
        }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::State;
    use std::env;
    use ureq;

    #[test]
    fn get_login_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/philips-hue/login").call();

        // Means login success! :)
        assert_eq!(resp.status(), 200);

        handle.stop();
    }

    #[test]
    fn create_login_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::put("http://0.0.0.0:8000/friday-vendor/philips-hue/login").call();

        // Means login success! :)
        assert_eq!(resp.status(), 200);

        handle.stop();

    }

    #[test]
    fn get_lights_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/philips-hue/lights").call();

        // Getting lights went fine!
        assert_eq!(resp.status(), 200);

        let lights : Vec<huelib::resource::Light> = 
            resp.into_json_deserialize::<Vec<serializeable_lights::Light>>()
            .expect("Failed to parse json response").into_iter().map(huelib::resource::Light::from).collect();
        friday_logging::info!("Lights response: {:?}", lights);

        handle.stop();
    }

    #[test]
    fn set_lights_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let update = LightUpdate {
            id: "4".to_owned(),
            state: State {
                on: Some(true),
                brightness: None,
                hue: None,
                saturation: None,
            }
        };

        let resp = ureq::put("http://0.0.0.0:8000/friday-vendor/philips-hue/lights")
            .send_json(serde_json::to_value(vec![update]).expect("Failed to serialize state"));

        // Setting lights went fine!
        assert_eq!(resp.status(), 200);

        handle.stop();
    }

    #[test]
    fn get_commands_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/friday-vendor/philips-hue/lights/commands").call();

        // Getting commands went fine!
        assert_eq!(resp.status(), 200);

        let commands : HashMap<String, Vec<LightUpdate>> = 
            resp.into_json_deserialize::<HashMap<String, Vec<LightUpdate>>>()
            .expect("Failed to parse json response");

        friday_logging::info!("commands response: {:?}", commands);

        handle.stop();
    }

    #[test]
    fn set_commands_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let hue_vendor = Hue::new().expect("Failed to create hue vendor");
        let web_hue_vendor = WebHue::new(&hue_vendor);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web_hue_vendor))
        ]).expect("Failed to register hue web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let mut update = std::collections::HashMap::<String, Vec<LightUpdate>>::new();
        update.insert("tänd ljuset".to_owned(), vec![
            LightUpdate {
                id: "4".to_owned(),
                state: State {
                    on: Some(true),
                    brightness: None,
                    hue: None,
                    saturation: None,
                }
            },
        ]);

        update.insert("släck ljuset".to_owned(), vec![
            LightUpdate {
                id: "4".to_owned(),
                state: State {
                    on: Some(false),
                    brightness: None,
                    hue: None,
                    saturation: None,
                }
            }
        ]);

        update.insert("godmorgon".to_owned(), vec![
            LightUpdate {
                id: "4".to_owned(),
                state: State {
                    on: Some(false),
                    brightness: None,
                    hue: None,
                    saturation: None,
                }
            }
        ]);



        let resp = ureq::put("http://0.0.0.0:8000/friday-vendor/philips-hue/lights/commands")
            .send_json(serde_json::to_value(update).expect("Failed to serialize state"));

        // Setting lights went fine!
        assert_eq!(resp.status(), 200);

        handle.stop();
    }

}
