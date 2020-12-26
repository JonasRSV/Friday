use crate::core::{
    HueCommandConfig, 
    LightUpdate,
    HueLogin, 
    HUE_LOGIN_TIMEOUT,
    HUE_USER, 
    HUE_CREDENTIAL_FILE, 
    HUE_CONFIG_FILE};
use friday_error::{frierr, propagate, FridayError};
use friday_storage;
use friday_logging;

use std::net::IpAddr;

use friday_vendor::Vendor;
use friday_vendor::DispatchResponse;
use huelib;

use std::sync::{Arc, Mutex, RwLock};

use std::time::Duration;
use std::time;




pub struct Hue {
    // Need to have this hidden behind locks
    // because they are also used by the webVendor
    // I have the bridge behind a lock because I am not sure if it
    // is thread-safe.. could maybe have two instances of it.. but this will be fine
    pub bridge: Arc<Mutex<Option<huelib::Bridge>>>,
    pub config: Arc<RwLock<HueCommandConfig>>,
}

impl Hue {
    /// Attempts to find a bridge on the local network
    fn find_bridge() -> Result<IpAddr, FridayError> {
        huelib::bridge::discover().map_or_else(
            |err| frierr!("Failed to discover bride - Reason: {}", err),
            |candidates: Vec<IpAddr>| candidates.first().map_or_else(
                || frierr!("Found no bridge available :("),
                |bridge_ip| Ok(bridge_ip.clone()))
        )
    }

    /// Queries the Hue bridge for new credentials
    fn query_for_credentials(ip: IpAddr, timeout: Duration) -> Result<HueLogin, FridayError> {
        let bridge_username : String;

        let timestamp = time::Instant::now();

        loop {

            let candidate_user = huelib::bridge::register_user(ip.clone(), HUE_USER);

            if candidate_user.is_ok() {
                bridge_username = candidate_user.unwrap();
                break;
            }

            if time::Instant::now().duration_since(timestamp).gt(&timeout) {
                return frierr!("Failed to aquire login - Reason: Login attempts timed out\n\n\
                This error most likely occurred because noone pressed the bridge in time");
            }

            friday_logging::info!("Please press the button on the bridge to let Friday register as a user...");
            std::thread::sleep(std::time::Duration::from_millis(2000));
        }

        return Ok(HueLogin {
            ip: ip.to_string(),
            user: bridge_username
        });
    }




    /// Finds the Hue Bridge and attempt to create a user
    pub fn create_hue_login() -> Result<HueLogin, FridayError> {
        Hue::find_bridge().map_or_else(
            propagate!("Unable create bridge login"),
            |ip| Hue::query_for_credentials(ip, Duration::from_secs(HUE_LOGIN_TIMEOUT)).map_or_else(
                propagate!("Unable to create bridge login"),
                |login| {
                    let write_res = friday_storage::config::write_config(&login, 
                        HUE_CREDENTIAL_FILE);

                    if write_res.is_err() {
                        friday_logging::warning!("Failed to store hueLogin - Reason: {:?} continuing anyway..", 
                            write_res.err().unwrap());
                    }

                    return Ok(login);
                }))

    }


    /// Attempt to read the login from a configuration file
    pub fn get_hue_login() -> Result<HueLogin, FridayError> {
        friday_storage::config::get_config(HUE_CREDENTIAL_FILE).map_or_else(
            propagate!("Failed to get hue login"),
            |login| Ok(login))
    }

    /// Attempt to read the command config from a configuration file
    fn get_command_config() -> Result<HueCommandConfig, FridayError> {
        return friday_storage::config::get_config(HUE_CONFIG_FILE);
    }


    /// Creates a new Hue Vendor
    /// If we cannot get the command config we crash
    /// If we cannot login right now that is fine
    /// We let users login at a later point using the UI
    /// we represent not being logged in by the HueBridge being 'None'
    /// when we're logged in it will be Some(bridge)
    pub fn new() -> Result<Hue, FridayError> {
        Hue::get_command_config().map_or_else(
            propagate!("Failed to create hue vendor"),
            |config| {
                let config_ref = &config;
                Hue::get_hue_login().map_or_else(
                    |_| Ok(Hue {
                        bridge: Arc::new(Mutex::new(None)),
                        config: Arc::new(RwLock::new(config_ref.clone()))
                    }),
                    |login| Ok(Hue {
                        bridge: Arc::new(
                                    Mutex::new(
                                        Some(
                                            huelib::Bridge::new(
                                                IpAddr::V4(login.ip.parse().unwrap()), 
                                                login.user)
                                        )
                                    )
                                ),
                                config: Arc::new(RwLock::new(config_ref.clone()))
                    }))

            })

    }
}

pub fn execute_light_updates(bridge: &huelib::Bridge, updates :&Vec<LightUpdate>) 
    -> Result<(), FridayError> {
    let mut err = FridayError::new("Things to try:\n \
                 0. Your hue credential file might have become invalid - try removing it");

    for update in updates.iter() {
        let mut modifier = huelib::resource::light::StateModifier::new();

        modifier = match update.state.on {
            Some(is_on) => modifier.with_on(is_on),
            None => modifier
        };

        modifier = match update.state.brightness {
            Some(brightness) => modifier.with_brightness(
                huelib::resource::Adjust::Override(brightness)),
            None => modifier
        };

        modifier = match update.state.hue {
            Some(hue) => modifier.with_hue(
                huelib::resource::Adjust::Override(hue)),
            None => modifier
        };

        modifier = match update.state.saturation {
            Some(saturation) => modifier.with_saturation(
                huelib::resource::Adjust::Override(saturation)),
            None => modifier
        };

        let result = bridge.set_light_state(update.id.clone(), &modifier);
        if result.is_err() {
            err = err.push(format!("Error occurred while setting lamp: {} - Error: {}", 
                    update.id.clone(), 
                    result.err().unwrap().to_string()));
        }
    }

    if err.len() > 1 {
        return Err(err);
    }

    return Ok(());
}

impl Vendor for Hue {
    fn name(&self) -> String { "philips-hue".to_owned() }
    fn dispatch(&self, action : &String) -> Result<DispatchResponse, FridayError> {
        match self.bridge.lock() {
            Err(err) => frierr!("Unable to aquire lock for hue bridge - Reason: {}", err),
            Ok(maybe_bridge) => match *maybe_bridge {
                None => frierr!("Hue Bridge has not yet been created\n\
                Things to try\n\
                1. Login via UI\n\
                2. Create appropriate configuration file and restart friday\n\
                "),
                Some(ref bridge) => 
                    match self.config.read() {
                        Err(err) => frierr!("Unable to aquire config - Reason: {}", err),
                        Ok(config) => config.lights.get(action).map_or_else(
                            || Ok(DispatchResponse::NoMatch), // Did not find command
                            |updates| execute_light_updates(bridge, updates)
                                        .map(|_| DispatchResponse::Success))

                    }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    #[test]
    fn create_login() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        Hue::create_hue_login().expect("Failed to get login");
    }

    #[test]
    fn command_config() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        Hue::get_command_config().expect("Failed to get command config");
    }

    #[test]
    fn dispatch_light_command() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        let vendor = Hue::new().expect("Failed to create hue vendor");
        vendor.dispatch(&"tänd ljuset".to_owned()).expect("Failed to dispatch");
        friday_logging::info!("hello");
    }
}
