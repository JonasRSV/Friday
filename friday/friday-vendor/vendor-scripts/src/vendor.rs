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
    scripts: HashMap<String, String>
}

pub struct Scripts {
    pub config: Arc<RwLock<Config>>
}

/// Enum type for the lookup function to differentiate between
/// Errors and missing action.
pub enum Lookup {
    Script(String),
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
            |config: Config| Ok(Scripts {
                config: Arc::new(RwLock::new(config)) 
            }))
    }

    fn lookup<S: AsRef<str>>(&self, name: S) -> Lookup {
        match self.config.read() {
            Err(err) => frierr!("Failed to read 'Scripts' config - Reason: {}", err), 
            Ok(config) =>  
                match config.scripts.get(name.as_ref()) {
                    None => Lookup::Missing,
                    Some(script) => Lookup::Script(script.to_owned())
                }
        }
    }

    /// Executes 'script' this blocks until exit
    /// Throws an error if the program has a non-zero exit code
    fn execute(&self, script: String) -> Result<DispatchResponse, FridayError> {
        friday_logging::info!("Executing {}", script);
        process::Command::new(script.clone()).output().map_or_else(
            |err| frierr!("Failed to execute {} - Reason: {}", script, err), 
            |output| {
                if output.status.success() {
                    friday_logging::info!("Executed {}", script);
                    Ok(DispatchResponse::Success)
                } else {
                    match std::str::from_utf8(&output.stdout) {
                        Err(err) => frierr!("Failed to convert process 'stdout' to utf8 - Reason: {}", err),
                        Ok(stdout) => frierr!("{} non-zero exit code {} - Process output: {}", 
                            script,
                            output.status.code().unwrap_or(-1),
                            stdout)
                    }
                }

            })
    }
}

impl Vendor for Scripts {
    fn name(&self) -> String { "scripts".to_owned() }
    fn dispatch(&self, action : &String) -> Result<DispatchResponse, FridayError> {
        match self.lookup(action) {
            Lookup::Missing => Ok(DispatchResponse::NoMatch),
            Lookup::Err(err) => err.into(),
            Lookup::Script(script) => self.execute(script)
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lookup_script() {
        let scripts = Scripts::new().expect("Failed to create 'Scripts' Vendor");

        match scripts.lookup("exists") {
            Lookup::Script(script) => assert_eq!(script, "./test-resources/woo.sh"),
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
            Lookup::Script(script) => {
                friday_logging::error!("{} should be missing, but contains {}", "no-exists", script);
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
    fn execute_script() {
        let scripts = Scripts::new().expect("Failed to create 'Scripts' Vendor");

        scripts.execute("./test-resources/woo.sh".to_owned()).expect("failed to execute woo");

        assert!(scripts.execute("./test-resources/noo.sh".to_owned()).is_err());

        let err = scripts.execute("./test-resources/bad_exit_code.sh".to_owned());
        assert!(err.is_err());

        friday_logging::error!("err is {:?}", err.err().unwrap());
    }
}
