use std::path;
use friday_error::{FridayError, frierr};
use wav;
use std::fs::File;  
use std::fs;

pub struct Files {
    root: path::PathBuf
}

impl Files {
    pub fn new(root: path::PathBuf) -> Result<Files, FridayError> {
        if root.is_dir() {
            Ok(Files {
                root
            })
        } else {
            frierr!("Failed to create 'Files' storage, Reason: {:?} is not a directory", root)
        }
    }

    /// Stores the audio data as a file named 'name'
    /// If successful returns Ok('name'.wav)
    pub fn store_audio<S: AsRef<str>>(&self, name: S, data: Vec<i16>, sample_rate: u32) -> Result<String, FridayError> {
        let file_name = name.as_ref().to_owned() + ".wav";
        let mut file_path = self.root.clone();

        file_path.push(file_name.clone());

        match File::create(file_path.clone()) {
            Err(err) => frierr!("Failed to create file {:?} for storing audio, Reason: {:?}", file_path, err),
            Ok(mut file) => 
                match wav::write(wav::Header::new(1, 1, sample_rate, 16), wav::BitDepth::Sixteen(data), &mut file) {
                    Err(err) => frierr!("Failed to write data to wav file, Reason: {:?}", err),
                    Ok(_) => Ok(file_name)
                }
        }
    }

    /// Tries to remove the file identified by 'name'
    pub fn remove_file<S: AsRef<str>>(&self, name: S) -> Result<(), FridayError> {
        let mut file_path = self.root.clone();
        file_path.push(name.as_ref());

        match fs::remove_file(file_path.clone()) {
            Err(err) => frierr!("Failed to remove file {:?}, Reason: {:?}", file_path, err),
            Ok(_) => Ok(())
        }
    }

    /// Tries to rename the node identified by 'old_name' to 'new_name'
    pub fn rename<S: AsRef<str>>(&self, old_name: S, new_name: S) -> Result<(), FridayError> {
        let mut old_path = self.root.clone();
        old_path.push(old_name.as_ref());

        let mut new_path = self.root.clone();
        new_path.push(new_name.as_ref());

        match fs::rename(old_path.clone(), new_path.clone()) {
            Err(err) => frierr!("Failed to move node {:?} to {:?}, Reason: {:?}", old_path, 
                new_path, err),
            Ok(_) => Ok(())
        }
    }

    /// Checks that a file or directory exists
    pub fn exists<S: AsRef<str>>(&self, name: S) -> bool {
        let mut path = self.root.clone();
        path.push(name.as_ref());
        path.exists()
    }   

    /// Lists all files under "namespace"
    pub fn list_files_under<S: AsRef<str>>(&self, namespace: S) -> Result<Vec<String>, FridayError> {
        let mut namespace_path = self.root.clone();
        namespace_path.push(namespace.as_ref());

        match namespace_path.read_dir() {
            Err(err) => frierr!("Failed to read directory {:?}, Reason {:?}", namespace_path, err),
            Ok(it) => {
                let mut names = Vec::new();
                for entry in it {
                    // As soon as one error occurs we fail
                    match entry {
                        Err(err) => return frierr!("Failed to read directory entry, Reason: {:?}", err),
                        Ok(e) => match e.file_name().into_string() {
                            Err(osstr) => return frierr!("Failed to convert {:?} into String", osstr),
                            Ok(r) => names.push(r)
                        }
                    };


                }

                Ok(names)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use crate::config;

    #[test]
    fn test_file_exists() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let config_dir = config::get_config_directory().expect("failed to get config directory");
        let files = Files::new(config_dir).expect("Failed to create 'Files' storage");
        assert!(files.exists("test_file"));
        assert!(!files.exists("doo"));

    }

    #[test]
    fn test_file_rename() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let config_dir = config::get_config_directory().expect("failed to get config directory");
        let files = Files::new(config_dir).expect("Failed to create 'Files' storage");

        files.rename("test_file", "some_file").expect("Failed to rename file");
        assert!(!files.exists("test_file"));
        assert!(files.exists("some_file"));

        files.rename("some_file", "test_file").expect("Failed to rename file");
        assert!(files.exists("test_file"));
        assert!(!files.exists("some_file"));
    }

    #[test]
    fn test_file_remove() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let config_dir = config::get_config_directory().expect("failed to get config directory");
        let files = Files::new(config_dir).expect("Failed to create 'Files' storage");

        File::create("./test-resources/tmp_file").expect("Failed to create file");
        assert!(files.exists("tmp_file"));

        files.remove_file("tmp_file").expect("Failed to remove tmp_file");
        assert!(!files.exists("tmp_file"));

    } 

    #[test]
    fn test_file_store_audio() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let config_dir = config::get_config_directory().expect("failed to get config directory");
        let files = Files::new(config_dir).expect("Failed to create 'Files' storage");

        let mut data: Vec<i16> = vec![0; 16000];
        for i in 0..16000 {
            data[i] = (((i as f32) / 1.0).sin() * 1000.0) as i16;
        }

        files.store_audio("audio_test", data, 8000).expect("Failed to store audio");

        assert!(files.exists("audio_test.wav"));

        files.remove_file("audio_test.wav").expect("Failed to remove audio_test.wav");
        assert!(!files.exists("audio_test.wav"));

    }

    #[test]
    fn test_file_list_namespace() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let config_dir = config::get_config_directory().expect("failed to get config directory");
        let files = Files::new(config_dir).expect("Failed to create 'Files' storage");

        assert_eq!(files.list_files_under("").expect("Failed to list files"), 
            vec!["test_config.json", "test_file"]);


    }


}
