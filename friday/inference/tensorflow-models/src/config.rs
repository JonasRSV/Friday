use std::path::{PathBuf, Path};
use std::env;
use std::collections::HashMap;
use serde_json;
use serde_derive::Deserialize;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;

#[derive(Deserialize)]
struct DiscriminativeJsonConfig {
    export_dir: String,
    class_map: String,
    sensitivity: f64
}

pub struct Discriminative {
    pub export_dir: PathBuf,
    pub class_map: Vec<String>,
    pub sensitivity: f64

}

fn get_file(file: String, root_path: &Path) -> Option<PathBuf> {
    for maybe_path in std::fs::read_dir(root_path).unwrap() {
        let path = maybe_path.unwrap();
        let file_name = path.file_name();
        if file_name.to_str().unwrap() == file {
            return Some(path.path());
        }
    }
    return None;

}

impl Discriminative {
    fn get_class_map(class_map_file: &String) -> Result<Vec<String>, FridayError> {
        // Open class_map json file

        let class_map_file_name = class_map_file.clone();

        std::fs::read_to_string(class_map_file.clone()).map_or_else(
            |_| frierr!("Unable to read file {}", class_map_file_name),
            |contents| serde_json::from_str(&contents).map_or_else(
                |err| frierr!("Unable to parse json in {} - Reason: {}", class_map_file_name, err),
                |class_map: HashMap<String, i32>| {
                    let mut class_map_mappings_vec: Vec<(String, i32)> = class_map
                        .iter()
                        .map(|k| (k.0.clone(), k.1.clone()))
                        .collect();

                    class_map_mappings_vec.sort_by_key(|k| k.1);

                    // Finally we have the class_map
                    return Ok(class_map_mappings_vec.iter().map(|k| k.0.clone()).collect());

                }))


    }

    fn get_discriminative(map: &DiscriminativeJsonConfig) -> Result<Discriminative, FridayError> {
        let maybe_class_map = Discriminative::get_class_map(&map.class_map);

        return maybe_class_map.map_or_else(
            |err| err.push("Could not to load class map for discriminative model").into(),
            |class_map| return Ok(
                Discriminative {
                    export_dir: PathBuf::from(map.export_dir.clone()),
                    class_map,
                    sensitivity: map.sensitivity
                }));
    }

    fn read_config(config_file: PathBuf) -> Result<Discriminative, FridayError> {
        let debug_file = config_file.clone();
        let file_name = debug_file.file_name().unwrap().to_str().unwrap();


        return std::fs::read_to_string(config_file)
            .map_or_else(
                |_| frierr!("Unable to read file {}", file_name),
                |contents| serde_json::from_str(&contents)
                .map_or_else(
                    |err| frierr!("Unable to parse json in {}, reason: {}", file_name, err),
                    |map: DiscriminativeJsonConfig| Discriminative::get_discriminative(&map) 
                )

            );
    }

    pub fn new() -> Result<Discriminative, FridayError> {
        return env::var("FRIDAY_CONFIG").map_or_else(
            |_| frierr!("The environment variable \
            FRIDAY_CONFIG needs to point to a configuration directory.\
            \nPlease set the FRIDAY_CONFIG environment variable.\
            \n\n\
            For example: \n\
            FRIDAY_CONFIG=./configs"),
            |config_path| {
                let path = PathBuf::from(config_path.clone());
                if ! path.is_dir() {
                    return frierr!("{} is not a valid directory", config_path)
                }

                let config_file_name = "discriminative.json";
                get_file(String::from(config_file_name),
                path.as_path()).map_or_else(
                || frierr!("{}/{} does not exist", config_path, config_file_name),
                Discriminative::read_config)
            }
        );
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn config_loading() {
        Discriminative::new().expect("Failed to read config");
    }
}
