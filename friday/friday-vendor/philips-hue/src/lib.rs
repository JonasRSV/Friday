use std::collections::HashMap;
use std::net::IpAddr;

use friday_error::frierr;
use friday_error::propagate;
use friday_error::FridayError;
use friday_storage;

use serde_derive::{Deserialize, Serialize};

use friday_vendor::Vendor;
use friday_vendor::DispatchResponse;
use huelib;

pub struct Hue {
    bridge: huelib::Bridge,
    commands: HueCommandConfig
}

// TODO, is this unsafe?
static HUE_CREDENTIAL_FILE: &str = "philips_hue_credentials.json";
static HUE_CONFIG_FILE: &str = "philips_hue.json";
static HUE_USER : &str = "friday-voice-assistant";

#[derive(Deserialize, Serialize)]
struct HueLogin {
    ip: String,
    user: String
}

#[derive(Deserialize, Clone)]
enum State {
    On,
    Off
}

#[derive(Deserialize, Clone)]
struct HueCommand {
    id: String,
    dispatch: State
}

#[derive(Deserialize)]
struct HueCommandConfig {
    hue_config: HashMap<String, Vec<HueCommand>>
}

impl Hue {
    // TODO add callback to this to support UI functionality at some point - or let the UI handle
    // this part.
    fn find_bridge() -> Result<HueLogin, FridayError> {
        huelib::bridge::discover().map_or_else(
            |err| frierr!("Failed to discover bride - Reason: {}", err),
            |candidates: Vec<IpAddr>| 
            candidates.first().map_or_else(
                || frierr!("Found no bridge available :("),
                |bridge_ip| {
                    let bridge_username : String;
                    loop {
                        let candidate_user = huelib::bridge::register_user(bridge_ip.clone(), HUE_USER);

                        if candidate_user.is_ok() {
                            bridge_username = candidate_user.unwrap();
                            break;
                        }

                        println!("Please press the button on the bridge to let Friday register as a user...");
                        std::thread::sleep(std::time::Duration::from_millis(2000));

                    }

                    return Ok(HueLogin {
                        ip: bridge_ip.to_string(),
                        user: bridge_username
                    });
                })
        )
    }


    fn get_hue_login() -> Result<HueLogin, FridayError> {
        return match friday_storage::config::get_config(HUE_CREDENTIAL_FILE) {
            Ok(login) => Ok(login),
            Err(mut load_err) => Hue::find_bridge().map_or_else(
                |bridge_err| friday_error::merge(&mut load_err, &bridge_err).into(),
                |hue_login| {
                    let write_res = friday_storage::config::write_config(&hue_login, HUE_CREDENTIAL_FILE);

                    if write_res.is_err() {
                        eprintln!("Failed to store hueLogin - Reason: {:?} continuing anyway..", 
                            write_res.err().unwrap());
                    }

                    return Ok(hue_login);
                })
        };
    }

    fn get_command_config() -> Result<HueCommandConfig, FridayError> {
        return friday_storage::config::get_config(HUE_CONFIG_FILE);
    }


    pub fn new() -> Result<Hue, FridayError> {
        return Hue::get_hue_login().map_or_else(
            propagate!("Failed to create hue vendor"),
            |credentials| Hue::get_command_config().map_or_else(
                propagate!("Failed to get command config"),
                |commands| Ok(Hue{
                    bridge: huelib::Bridge::new(IpAddr::V4(credentials.ip.parse().unwrap()), credentials.user),
                    commands
                })));
    }
}

impl Vendor for Hue {
    fn dispatch(&self, action : &String) -> DispatchResponse {
        return self.commands.hue_config.get(action).map_or_else(
            || DispatchResponse::NoMatch,
            |commands| {
                let mut err = FridayError::new("Hue errors");

                for command in commands.iter() {
                    let mut modifier = huelib::resource::light::StateModifier::new();

                    modifier = match command.clone().dispatch {
                        State::On => modifier.with_on(true),
                        State::Off => modifier.with_on(false)
                    };

                    let result = self.bridge.set_light_state(command.id.clone(), &modifier);
                    if result.is_err() {
                        err = err.push(format!("Error occurred while setting lamp: {}", 
                                command.id.clone()));
                        err = err.push(format!("{}", result.err().unwrap()));
                        err = err.push("Things to try:\n \
                        1. Your hue credential file might have become invalid - try removing it");
                    }
                }

                if err.len() > 1 {
                    return DispatchResponse::Err {
                        err
                    }
                }

                return DispatchResponse::Success;

            });
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    #[test]
    fn get_login() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        Hue::get_hue_login().expect("Failed to get login");
    }

    #[test]
    fn command_config() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        Hue::get_command_config().expect("Failed to get command config");
    }
}
