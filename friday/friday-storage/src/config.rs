use serde;
use serde_json;
use std::env;
use friday_error::frierr;
use friday_error::propagate;
use friday_error::FridayError;
use std::path::PathBuf;
use std::fs;

pub fn get_config_directory() -> Result<PathBuf, FridayError> {
    return env::var("FRIDAY_CONFIG").map_or_else(
        |_| frierr!("The environment variable FRIDAY_CONFIG needs to point \
                to a configuration directory. \nPlease set the FRIDAY_CONFIG environment variable.\
                \n\n\
                For example: \n\
                FRIDAY_CONFIG=./configs"),
                |config_path_string| {
                    let path = PathBuf::from(config_path_string.clone());

                    if path.is_dir() {
                        return Ok(path);
                    } else {
                        return frierr!("{} is not a valid path", config_path_string);

                    }
                });

}

pub fn get_config<T, S>(name: S) -> Result<T, FridayError>
where T: serde::de::DeserializeOwned,
      S: AsRef<str> {
          return get_config_directory().map_or_else(
              propagate!("Failed to get config directory when reading config"),
              |config_path| {
                  let mut path_to_file = config_path.clone();
                  path_to_file.push(name.as_ref());
                  fs::read_to_string(&path_to_file).map_or_else(
                      |err| frierr!("Failed to read {} - Reason: {}", path_to_file.to_str().unwrap(), err),
                      |contents| serde_json::from_str(&contents).map_or_else(
                          |err| frierr!("Failed to deserialize config {} - Reason: {}", 
                              path_to_file.to_str().unwrap(), err),
                          |conf| Ok(conf)
                      ))
              });
}

pub fn write_config<T, S>(o: &T, name: S) -> Result<(), FridayError>
where T: serde::Serialize,
      S: AsRef<str> {
          return serde_json::to_string_pretty(o).map_or_else(
              |err| frierr!("Failed to serialize into json - Reason {}", err),
              |json| get_config_directory().map_or_else(
                  propagate!("Failed to get config directory when writing config"),
                  |config_path| {
                      let mut path_to_file = config_path.clone();
                      path_to_file.push(name.as_ref());
                      return fs::write(path_to_file, json).map_or_else(
                          |err| frierr!("Failed to write config to {} - Reason: {}", 
                              config_path.to_str().unwrap(), err),
                              |_| Ok(()))
                  }));
}


#[cfg(test)]
mod tests {
    use super::*;
    use serde_derive::{Deserialize, Serialize};

    #[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
    enum TestEnum {
        On,
        Off
    }

    #[derive(Deserialize, Serialize)]
    struct TestConfig {
        ip: String,
        user: String,
        action: TestEnum

    }

    #[test]
    fn write_load_simple_config() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let conf: TestConfig = TestConfig{
            ip: String::from("0.0.0.0"),
            user: String::from("wolololo"),
            action: TestEnum::On
        };

        write_config(&conf, "test_config.json").expect("Writing config failed");
        let read_conf: TestConfig = get_config("test_config.json").expect("Reading config failed");

        assert_eq!(read_conf.ip, conf.ip);
        assert_eq!(read_conf.user, conf.user);
        assert_eq!(read_conf.action, conf.action);

    }

}
