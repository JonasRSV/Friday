use std::{collections::HashMap, env};
use std::net::{IpAddr, Ipv4Addr};
use std::path::{PathBuf, Path};
use std::fs;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;

use serde_json;
use serde_derive::{Deserialize, Serialize};

use vendor_io::Vendor;
use vendor_io::DispatchResponse;
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
    fn find_bridge_and_create_user() -> Result<HueLogin, FridayError> {
        huelib::bridge::discover().map_or_else(
            |err| frierr!("Failed to discover bride - Reason: {}", err),
            |candidates: Vec<IpAddr>| 
            candidates.first().map_or_else(
                || frierr!("Found no bridge available :("),
                |bridge_ip| {
                    let mut bridge_username : String = String::new();
                    loop {
                        let candidate_user = huelib::bridge::register_user(bridge_ip.clone(), HUE_USER);

                        if candidate_user.is_ok() {
                            bridge_username = candidate_user.unwrap();
                            break;
                        }

                        println!("Please press the button on the bridge to let Friday register as a user...");
                        std::thread::sleep(std::time::Duration::from_millis(2000));

                    }

                    println!("Successfully Created a User! :)");
                    return Ok(HueLogin {
                        ip: bridge_ip.to_string(),
                        user: bridge_username
                    });
                })
        )
    }

    fn save_login_to_file(login: &HueLogin, path: &Path) -> Result<(), FridayError> {
        return serde_json::to_string(login).map_or_else(
            |err| frierr!("Failed to serialize login to string {}", err),
            |string| fs::write(path, string).map_or_else(
                |err| frierr!("Failed to write to file {} - Reason: {}", path.to_str().unwrap(), err),
                |_| Ok(println!("Created credentials at {}", path.to_str().unwrap()))
            ));
    }

    fn load_login_from_file(file: &Path) -> Result<HueLogin, FridayError> {
        return fs::read_to_string(file).map_or_else(
            |err| frierr!("Failed to read file {} - Reason: {}", file.to_str().unwrap(), err),
            |content| serde_json::from_str(&content).map_or_else(
                |err| frierr!("Failed to parse hue login file {}: Reason - {}", file.to_str().unwrap(), err),
                |login| Ok(login)));
    }

    fn get_hue_login() -> Result<HueLogin, FridayError> {
        return env::var("FRIDAY_CONFIG").map_or_else(
            |_| frierr!("The environment variable FRIDAY_CONFIG needs to point \
            to a configuration directory. \nPlease set the FRIDAY_CONFIG environment variable.\
            \n\n\
            For example: \n\
            FRIDAY_CONFIG=./configs"),
            |config_path| {
                let path = PathBuf::from(config_path.clone());
                if ! path.is_dir() {
                    return frierr!("{} is not a valid directory", config_path);
                }


                let mut path_to_file = path.clone();
                path_to_file.push(HUE_CREDENTIAL_FILE);

                if path_to_file.is_file() {
                    return Hue::load_login_from_file(&path_to_file);
                } else {
                    println!("{}/{} does not exist -- I will try to create it", 
                        config_path, HUE_CREDENTIAL_FILE);

                    return Hue::find_bridge_and_create_user().map_or_else(
                        |err| err.push("Failed to create philips hue config").into(),
                        |login| Hue::save_login_to_file(&login, path_to_file.as_path()).map_or_else(
                            |err| err.push("Failed to save login to file").into(),
                            |_| Ok(login)));
                }
            })
    }

    fn load_command_config_from_file(file: &Path) -> Result<HueCommandConfig, FridayError> {
        return fs::read_to_string(file).map_or_else(
            |err| frierr!("Failed to read file {} - Reason: {}", file.to_str().unwrap(), err),
            |content| serde_json::from_str(&content).map_or_else(
                |err| frierr!("Failed to parse hue login file {}: Reason - {}", 
                    file.to_str().unwrap(), 
                    err),
                    |login| Ok(login)));
    }

    fn get_command_config() -> Result<HueCommandConfig, FridayError> {
        return env::var("FRIDAY_CONFIG").map_or_else(
            |_| frierr!("The environment variable FRIDAY_CONFIG needs to point \
            to a configuration directory. \nPlease set the FRIDAY_CONFIG environment variable.\
            \n\n\
            For example: \n\
            FRIDAY_CONFIG=./configs"),
            |config_path| {
                let path = PathBuf::from(config_path.clone());
                if ! path.is_dir() {
                    return frierr!("{} is not a valid directory", config_path)
                }


                let mut path_to_file = path.clone();
                path_to_file.push(HUE_CONFIG_FILE);

                if path_to_file.is_file() {
                    return Hue::load_command_config_from_file(&path_to_file);
                }

                return frierr!("{} is not a valid file", path_to_file.to_str().unwrap());
            })
    }

    pub fn new() -> Result<Hue, FridayError> {
        return Hue::get_hue_login().map_or_else(
            |err| err.push("Failed to create Hue Vendor").into(),
            |credentials| Hue::get_command_config().map_or_else(
                |err| err.push("Failed to get command config").into(),
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
    #[test]
    fn get_login() {
        Hue::get_hue_login().expect("Failed to get login");
    }

    #[test]
    fn command_config() {
        Hue::get_command_config().expect("Failed to get command config");
    }
}
