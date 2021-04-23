use friday_vendor::Vendor;
use friday_vendor::DispatchResponse;
use friday_error::{FridayError, propagate, frierr};
use friday_storage;
use friday_logging;
use std::collections::HashMap;

use std::sync::{Arc, RwLock};
use std::process;

use serde_derive::{Deserialize, Serialize};

#[derive(Deserialize, Serialize)]
pub struct Config {
    pub scripts: HashMap<String, Vec<String>>
}

pub struct Scripts {
    pub config: Arc<RwLock<Config>>,
    pub files: friday_storage::files::Files
}

/// Enum type for the lookup function to differentiate between
/// Errors and missing action.
pub enum Lookup {
    Scripts(Vec<String>),
    Missing,
    Err(FridayError)
}

/// Auto convertion from fridayErrors into lookups
impl Into<Lookup> for FridayError {
    fn into(self) -> Lookup {
        return Lookup::Err(self);
    }
}


impl Scripts {
    /// The scripts vendor lets you execute your own scripts 
    /// on keyword triggers.
    pub fn new() -> Result<Scripts, FridayError> {
        friday_storage::config::get_config("scripts.json").map_or_else(
            propagate!("Failed to create new scripts vendor"), 
            |config: Config| Scripts::from_config(config))
    }

    fn from_config(config: Config) -> Result<Scripts, FridayError> {
        friday_storage::config::get_config_directory().map_or_else(
            propagate!("Failed to create get config directory for 'Scripts' Vendor"), 
            |mut config_dir| {
                // We store all scripts in 'CONFIG_ROOT/recordings'
                config_dir.push("scripts");
                friday_storage::files::Files::new(config_dir).map_or_else(
                    propagate!("Failed to create 'Files' for 'Scripts' vendor"),
                    |files| Ok(Scripts {
                        config: Arc::new(RwLock::new(config)),
                        files
                    }))})

    }

    fn lookup<S: AsRef<str>>(&self, name: S) -> Lookup {
        match self.config.read() {
            Err(err) => frierr!("Failed to read 'Scripts' config - Reason: {}", err), 
            Ok(config) =>  
                match config.scripts.get(name.as_ref()) {
                    None => Lookup::Missing,
                    Some(scripts) => Lookup::Scripts(scripts.to_owned())
                }
        }
    }

    /// Executes 'script' this blocks until exit
    /// Throws an error if the program has a non-zero exit code
    fn execute(&self, script: String) {
        friday_logging::info!("Executing {}", script);

        match self.files.full_path_of(script.clone()) {
            Err(err) => friday_logging::error!("Failed to execute {}, Reason: {:?}", script, err),
            Ok(command) => process::Command::new(command.clone()).output().map_or_else(
                |err| friday_logging::error!("Failed to execute {}, Reason: {}", command.clone(), err), 
                |output| {
                    if output.status.success() {
                        friday_logging::info!("Successfully Executed {}", script);
                    } else {
                        match std::str::from_utf8(&output.stdout) {
                            Err(err) => friday_logging::error!(
                                "Failed to convert process 'stdout' to utf8 - Reason: {}", err),
                            Ok(stdout) => friday_logging::error!(
                                "{} non-zero exit code {} - Process output: {}", 
                                command.clone(),
                                output.status.code().unwrap_or(-1),
                                stdout)
                        }
                    }

                })
        }

    }
}

impl Vendor for Scripts {
    fn name(&self) -> String { "scripts".to_owned() }
    fn dispatch(&self, action : &String) -> Result<DispatchResponse, FridayError> {
        match self.lookup(action) {
            Lookup::Missing => Ok(DispatchResponse::NoMatch),
            Lookup::Err(err) => err.into(),
            Lookup::Scripts(scripts) => {
                scripts.iter().for_each(|script| self.execute(script.to_owned()));

                Ok(DispatchResponse::Success)
            }
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn lookup_scripts() {
        env::set_var("FRIDAY_CONFIG", "test-resources");
        let scripts = Scripts::from_config(
            Config {
                scripts: [
                    ("hello".to_owned(), vec!["woo.sh".to_owned()]),
                    ("what".to_owned(), vec!["woo".to_owned()]),
                ].iter().cloned().collect()
            }

        ).expect("Failed to create Scripts Vendor");

        match scripts.lookup("hello") {
            Lookup::Scripts(scripts) => assert_eq!(scripts, vec!["woo.sh"]),
            Lookup::Missing => {
                friday_logging::error!("Missing key 'exists'");
                assert!(false)
            }, 
            Lookup::Err(err) => {
                friday_logging::error!("{:?}", err);
                assert!(false)

            }
        }

        match scripts.lookup("no-exists") {
            Lookup::Scripts(scripts) => {
                friday_logging::error!("{} should be missing, but contains {:?}", "no-exists", scripts);
                assert!(false);
            },
            Lookup::Missing => assert!(true),
            Lookup::Err(err) => {
                friday_logging::error!("{:?}", err);
                assert!(false)

            }
        }
    }

    #[test]
    fn execute_scripts() {
        env::set_var("FRIDAY_CONFIG", "test-resources");

        let scripts = Scripts::from_config(Config{
            scripts: HashMap::new()
        }).expect("Failed to create 'Scripts' Vendor");

        scripts.execute("all-hue-off.py".to_owned());
        scripts.execute("woo.sh".to_owned());
        scripts.execute("hi_python.py".to_owned());
        scripts.execute("noo.sh".to_owned());
        scripts.execute("bad_exit_code.sh".to_owned());
        scripts.execute("boo.sh".to_owned());

    }

    #[test]
    fn execute_many_scripts() {
        env::set_var("FRIDAY_CONFIG", "test-resources");
        let scripts = Scripts::from_config(Config{
            scripts: [
                ("hello".to_owned(), vec!["woo.sh".to_owned(), "woo.sh".to_owned(), "bad_exit_code.sh".to_owned()]),
            ].iter().cloned().collect()
        }).expect("Failed to create 'Scripts' vendor");


        let script = "hello".to_owned();
        scripts.dispatch(&script).expect("Failed to dispatch");

    }
}
