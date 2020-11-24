use std::path::{PathBuf, Path};
use std::env;
use std::collections::HashMap;
use serde_json;

pub struct Discriminative {
    pub export_dir: PathBuf,
    pub class_map: Vec<String>
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
    fn get_class_map(m: &HashMap<String, String>) -> Vec<String> {
        // Open class_map json file
        let class_map_file = PathBuf::from(
            m.get("class_map")
            .expect("discriminative_config did not contain field 'class_map'"));

        let class_map_text_content = 
            std::fs::read_to_string(class_map_file.clone()).expect(
                format!("Unable to open class_map: {}", 
                    class_map_file.to_str().unwrap(
                    )).as_ref());

        let class_map_mappings: HashMap<String, i32> = 
            serde_json::from_str(&class_map_text_content)
            .expect("Failed to parse JSON");

        // Extract Sorted map
        let mut class_map_mappings_vec: Vec<(String, i32)> = class_map_mappings
            .iter()
            .map(|k| (k.0.clone(), k.1.clone()))
            .collect();

        class_map_mappings_vec.sort_by_key(|k| k.1);

        // Finally we have the class_map
        return class_map_mappings_vec.iter().map(|k| k.0.clone()).collect();
    }

    fn get_export_dir(m: &HashMap<String, String>) -> PathBuf {
        // Open class_map json file
        return PathBuf::from(
            m.get("export_dir")
            .expect("discriminative_config did not contain field 'export_dir'"));
    }

    pub fn new() -> Discriminative {
        match env::var("FRIDAY_CONFIG") {
            Ok(config) => {
                let path = PathBuf::from(config);
                if !path.is_dir() {
                    eprintln!("\nFRIDAY_CONFIG does not point to a directory\n");
                    eprintln!("{} is not a directory\n\n", path.to_str().unwrap());
                    panic!("Exiting - could not load discriminative config..");
                }

                let discriminative_config_file = String::from("discriminative.json");

                // Open config json_file
                let discriminative_config = get_file(
                    discriminative_config_file.clone(), 
                    path.as_path()).expect(format!(
                        "{} not found in {}", 
                        discriminative_config_file.clone(),
                        path.to_str().unwrap()
                    ).as_ref()
                    );

                let discriminative_text_content = 
                    std::fs::read_to_string(discriminative_config.clone()).expect(
                        format!("Unable to open {}", 
                            discriminative_config.to_str().unwrap(
                            )).as_ref());

                let config_mappings: HashMap<String, String> = 
                    serde_json::from_str(&discriminative_text_content)
                    .expect("Failed to parse JSON");

                return Discriminative{
                    export_dir: Discriminative::get_export_dir(&config_mappings),
                    class_map: Discriminative::get_class_map(&config_mappings)
                };
            },
            Err(_) => {
                eprintln!("\nPlease set the environment variable FRIDAY_CONFIG\n");
                eprintln!("FRIDAY_CONFIG should contain a path to the config directory");
                eprintln!("For example in a shell: FRIDAY_CONFIG=./test-resources\n\n");
                eprintln!("The discriminative model uses this environment variable to load its deps\n\n");
                eprintln!("If you don't know what the config directory should contain leave it empty and run again, friday will complain until everything is right\n\n");
                panic!("Exiting - could not load discriminative config.. nothing more todo.");
            }

        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn config_loading() {
        Discriminative::new();
    }
}
