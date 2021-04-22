use crate::ddl::model as m;
use std::ffi::CString;
use float_ord::FloatOrd;

use friday_inference;

use friday_error::{frierr, propagate, FridayError};
use friday_logging;

use friday_storage;
use friday_web;

use std::path::PathBuf;
use std::collections::HashMap;
use std::sync::{Arc, RwLock, RwLockWriteGuard, Mutex};

use serde_derive::{Deserialize, Serialize};
use serde_json;


#[derive(Deserialize, Serialize, Clone)]
pub struct Config {
    export_dir: PathBuf,
    sensitivity: f32,

    // First entry is a file-name second is command name
    audio: HashMap<String, String>
}

#[derive(Debug, Clone)]
struct Examples {
    audio: HashMap<String, String>,

    // These are unique identifiers, likely the file name
    ids: Vec<String>,

    // These are the command names (friday, lights on, etc..)
    names: Vec<String>,

    // These are the projected audio files.
    embeddings: Vec<Vec<f32>>,
}

// This structure is shared between inference and webserver
struct DDLModel {
    model: m::Model,

    input_audio: m::Tensor,
    input_embeddings: m::Tensor,
    output_projection: m::Tensor,
    output_distances: m::Tensor,
}

unsafe impl Send for DDLModel { }


#[derive(Clone)]
pub struct DDL {
    model: Arc<Mutex<DDLModel>>,

    examples: Arc<RwLock<Examples>>,
    sensitivity: Arc<RwLock<f32>>,

    export_dir: PathBuf,

    frame_size: usize,

    files: friday_storage::files::Files
}

impl DDL {

    pub fn new() -> Result<DDL, FridayError>  {
        return friday_storage::config::get_config("ddl.json").map_or_else(
            propagate!("Failed to create ddl model"),
            DDL::model_from_config 
        );
    }
    fn model_from_config(config: Config) ->
        Result<DDL, FridayError> {
            let input_audio_op_name = CString::new("audio").unwrap();
            let input_embeddings_op_name = CString::new("embeddings").unwrap();
            let output_projection_op_name = CString::new("project").unwrap();
            let output_distances_op_name = CString::new("distances").unwrap();

            return m::Model::new(config.export_dir.as_path())
                .map_or_else(
                    || frierr!("Failed to create DDL"),
                    |model|  {
                        let input_audio = m::Tensor::new(&model, &input_audio_op_name);
                        let input_embeddings = m::Tensor::new(&model, &input_embeddings_op_name);

                        let output_projection = m::Tensor::new(&model, &output_projection_op_name);
                        let output_distances = m::Tensor::new(&model, &output_distances_op_name);

                        let frame_size = input_audio.dims
                            .first()
                            .expect("(tensorflow-models): Failed to extract input dims from model")
                            .clone() as usize;


                        friday_storage::config::get_config_directory().map_or_else(
                            propagate!("Failed to create DDL model"), 
                            |mut config_dir| {
                                // We store all recordings in 'CONFIG_ROOT/recordings'
                                config_dir.push("recordings");
                                friday_storage::files::Files::new(config_dir).map_or_else(
                                    propagate!("Failed to create DDL model"), 
                                    |files| {
                                        let model = DDL{
                                            model: Arc::new(Mutex::new(DDLModel{
                                                model,
                                                input_audio,
                                                input_embeddings,
                                                output_projection,
                                                output_distances,
                                            })),


                                            examples: Arc::new(RwLock::new(Examples {
                                                audio: config.audio,
                                                ids: Vec::new(),
                                                names: Vec::new(),
                                                embeddings: Vec::new()

                                            })),
                                            sensitivity: Arc::new(RwLock::new(config.sensitivity)),

                                            export_dir: config.export_dir,
                                            frame_size,
                                            files
                                        };

                                        // Run first sync to load audio files from disk
                                        match model.clone().sync() {
                                            Ok(()) => Ok(model),
                                            Err(err) => propagate!("Failed to create DDL model")(err)
                                        }
                                    }
                                )}
                        )
                    })
    }

    /// Runs the DDL models projection operation
    fn project(&mut self, audio: &Vec<i16>) -> Result<Vec<f32>, FridayError> {
        match self.model.lock() {
            Err(err) => frierr!("Failed to aquire lock for DDL model {}", err),
            Ok(model) => {
                let mut input_audio = model.input_audio.clone();
                let mut output_projection = model.output_projection.clone();

                input_audio.set_data(audio);

                model.model.clone().run_projection(
                    &mut input_audio, 
                    &mut output_projection
                );

                return Ok(output_projection.get_data::<f32>());

            }


        }

    }

    /// Adds a new example to the examples
    fn add(&mut self, examples: &mut RwLockWriteGuard<Examples>, name: &String, file_name: &String) {
        match self.files.read_audio(file_name) {
            Err(err) => friday_logging::error!("Failed to add example - file name: {} - Reason: {:?}", 
                file_name.clone(),
                err),
                Ok((audio, _)) => {
                    match self.project(&audio) {
                        Err(err) => friday_logging::error!("Failed to project using DDL model {:?}", err),
                        Ok(embedding) => {
                            examples.ids.push(file_name.to_owned());
                            examples.names.push(name.to_owned());
                            examples.embeddings.push(embedding);
                        }
                    }
                }
        }
    }

    /// Updates an exisiting example 
    fn update(&mut self, examples: &mut RwLockWriteGuard<Examples>, name: &String, file_name: &String, index: usize) {
        match self.files.read_audio(file_name) {
            Err(err) => friday_logging::error!("Failed to add example {:?}", err),
            Ok((audio, _)) => {
                match self.project(&audio) {
                    Err(err) => friday_logging::error!("Failed to project using DDL model {:?}", err),
                    Ok(embedding) => {
                        examples.ids[index] = file_name.to_owned();
                        examples.names[index] = name.to_owned();
                        examples.embeddings[index] = embedding;
                    }
                }
            }
        }
    }

    fn sync(&mut self) -> Result<(), FridayError> {
        match self.examples.clone().write() {
            Err(err) => frierr!("Failed to read RWLocked examples - Reason: {}", err),
            Ok(mut examples) => {

                let audio = examples.audio.clone();
                let ids = examples.ids.clone();
                let names = examples.names.clone();
                // Add or Update any new / existing examples
                for (file_name, name) in audio.iter() {
                    match ids.iter().position(|_id| _id == file_name) {
                        Some(id_index) => {

                            // This happends if for some reason an audio file is assigned a
                            // different keyword
                            if names[id_index] != name.to_owned() {
                                friday_logging::debug!("Updating example ({}, {}) -> ({}, {})",
                                    names[id_index], ids[id_index], name, file_name);
                                self.update(&mut examples, &name, &file_name, id_index)
                            }
                        },
                        // Audio file is not yet present as an example so we add it
                        None => {
                            friday_logging::debug!("Adding example ({}, {})", name, file_name);
                            self.add(&mut examples, &name, &file_name)
                        }
                    }
                }

                //// Remove any stale examples 
                for (index, id) in examples.ids.clone().iter().enumerate() {
                    if !examples.audio.contains_key(id) {
                        friday_logging::debug!("Removing example ({}, {})", names[index], ids[index]);
                        examples.names.remove(index);
                        examples.ids.remove(index);
                        examples.embeddings.remove(index);

                    }
                }


                Ok(())
            }
        }
    }
}

impl friday_inference::Model for DDL {
    fn predict(&mut self, v :&Vec<i16>) -> Result<friday_inference::Prediction, FridayError> {

        match self.model.lock() {
            Ok(model) => match self.examples.read() {
                Ok(examples) => match self.sensitivity.read() {
                    Ok(sensitivity) => {

                        if examples.embeddings.len() == 0 {
                            friday_logging::debug!("Cannot infer without examples");
                            return Ok(friday_inference::Prediction::Inconclusive);
                        }


                        let mut input_embeddings = model.input_embeddings.clone();
                        let mut input_audio = model.input_audio.clone();
                        let mut output_distances = model.output_distances.clone();

                        // Set the 'unknown' dimension
                        input_embeddings.dims[0] = examples.embeddings.len() as i64;
                        output_distances.dims[0] = examples.embeddings.len() as i64;

                        // set the data
                        input_audio.set_data(&v);
                        input_embeddings.set_data(&examples.embeddings);


                        // run inference
                        model.model.clone().run_distances(
                            &mut input_audio,
                            &mut input_embeddings, 
                            &mut output_distances);

                        let distances = output_distances.get_data::<f32>();

                        let min_distance_index = distances
                            .iter()
                            .enumerate()
                            .min_by_key(|k| FloatOrd(k.1.clone()))
                            .map(|k| k.0)
                            .expect("failed to get max").clone();

                        friday_logging::info!("D({}) = {}", examples.names[min_distance_index], 
                            distances[min_distance_index]);

                        if distances[min_distance_index] < sensitivity.clone() {
                            return Ok(friday_inference::Prediction::Result {
                                class: examples.names[min_distance_index].clone()
                            })
                        }

                        return Ok(friday_inference::Prediction::Inconclusive);

                    },
                    Err(err) => frierr!("Failed to read RWLocked sensitivity - Reason: {}", err)

                },
                Err(err) => frierr!("Failed to read RWLocked examples - Reason: {}", err)

            }
            Err(err) => frierr!("Failed to aquire lock for DDL model - Reason: {}", err)
        }

    }

    fn expected_frame_size(&self) -> usize {
        return self.frame_size;
    }
}

pub struct WebDDL{
    endpoints: Vec<friday_web::endpoint::Endpoint>,
    ddl: DDL,
}

impl WebDDL{
    pub fn new(d: &DDL) -> WebDDL{
        WebDDL {
            endpoints: vec![
                friday_web::endpoint::Endpoint{ 
                    name: "examples".to_owned(),
                    methods: vec![friday_web::core::Method::Get, friday_web::core::Method::Put],
                    path: friday_web::path::Path::safe_new(
                        "/friday-inference/tensorflow-models/ddl/examples")
                },
                friday_web::endpoint::Endpoint{ 
                    name: "sensitivity".to_owned(),
                    methods: vec![friday_web::core::Method::Get, friday_web::core::Method::Put],
                    path: friday_web::path::Path::safe_new(
                        "/friday-inference/tensorflow-models/ddl/sensitivity")
                }
            ],
            ddl: d.clone()
        }
    }

    fn get_examples(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.ddl.examples.read() {
            Ok(examples) => serde_json::to_string(&examples.audio.clone()).map_or_else(
                |err| frierr!(
                    "Failed to serialize examples audio - {:?} - to json - Reason: {}", 
                    examples.audio, 
                    err),
                    |content|  Ok(friday_web::core::Response::JSON {
                        status: 200, content 
                    })),

            Err(err) => frierr!("Failed to read RWLocked examples - Reason: {}", err)
        }
    }

    /// Update the audio examples used by the DDL model, sync the model and write to disk.
    fn set_examples(&self, audio: HashMap<String, String>) -> Result<friday_web::core::Response, FridayError> {
        // Update examples with new audio and create new configuration
        let config = match self.ddl.sensitivity.read() {
            Err(err) => frierr!("Failed to read RWLocked sensitivity - Reason: {}", err),
            Ok(sensitivity) => match self.ddl.examples.write() {
                Ok(mut examples) => {
                    examples.audio = audio.clone();

                    Ok(Config {
                        export_dir: self.ddl.export_dir.clone(),
                        sensitivity: sensitivity.clone(),
                        audio: audio.clone()
                    })
                }
                Err(err) => frierr!("Failed to write RWLocked examples - Reason: {}", err)
            }
        };

        // We have to split this into another match, otherwise we will get a deadlock with sync.
        // To create the config we lock the examples and update them.
        // Sync also does so, but the update lock must let go before we run sync
        //
        // Sync with new audio and write new configuration
        match config {
            Err(err) => propagate!("Failed to set examples")(err),
            Ok(config) => 
                match self.ddl.clone().sync() {
                    Err(err) => propagate!("Failed to sync DDL model")(err),
                    Ok(()) => match friday_storage::config::write_config(&config, "ddl.json") {
                        // Successfully stored commands - all is well in the world! 
                        Ok(_) => friday_web::ok!("All good!"),

                        // TODO: Think about what the best UX for this is
                        Err(err) => {
                            friday_logging::warning!("Failed to store new ddl config to disk - Reason: {:?}", 
                                err);

                            friday_web::ok!("Updated for this session - But failed to store on disk")
                        }
                    }
                }
        }
    }

    fn get_sensitivity(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.ddl.sensitivity.read() {
            Ok(sensitivity) => serde_json::to_string(&sensitivity.clone()).map_or_else(
                |err| frierr!(
                    "Failed to serialize sensitivity - {:?} - to json - Reason: {}", 
                    sensitivity, 
                    err),
                    |content|  Ok(friday_web::core::Response::JSON {
                        status: 200, content 
                    })),

            Err(err) => frierr!("Failed to read RWLocked sensitivity - Reason: {}", err)
        }
    }

    /// Set the sensitivity used by the DDL model
    fn set_sensitivity(&self, sensitivity_message: HashMap<String, f32>) -> Result<friday_web::core::Response, FridayError> {
        match self.ddl.examples.read() {
            Ok(examples) => match self.ddl.sensitivity.write() {
                Ok(mut sensitivity) => 
                    match sensitivity_message.get("sensitivity") {
                        Some(new_sensitivity) => {
                            *sensitivity = *new_sensitivity;

                            let config = Config {
                                export_dir: self.ddl.export_dir.clone(),
                                audio: examples.audio.clone(),
                                sensitivity: sensitivity.clone()
                            };

                            match friday_storage::config::write_config(&config, "ddl.json") {
                                // Successfully stored commands - all is well in the world! 
                                Ok(_) => friday_web::ok!("All good!"),

                                // TODO: Think about what the best UX for this is
                                Err(err) => {
                                    friday_logging::warning!("Failed to store new ddl config to disk - Reason: {:?}", 
                                        err);

                                    friday_web::ok!("Updated for this session - But failed to store on disk")
                                }
                            }
                        },
                        None => frierr!("Sensitivity message {:?} missing field 'sensitivity'", sensitivity_message)
                    }
                Err(err) => frierr!("Failed to write RWLocked sensitivity - Reason: {}", err)
            }
            Err(err) => frierr!("Failed to read RWLocked Examples - Reason: {}", err)
        }
    }

}

impl friday_web::vendor::Vendor for WebDDL {
    fn name(&self) -> String { return "friday-inference/tensorflow-models/ddl".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> Result<friday_web::core::Response, FridayError> {
        match friday_web::get_name(r, &self.endpoints) {
            Err(err) => propagate!("Failed to get 'DDL' endpoint for {}", r.url())(err),
            Ok(name) => match name.as_str() {
                "examples" => match r.method() {
                    friday_web::core::Method::Get => self.get_examples(),     // This gets the commands
                    // This updates the commands and stores updates to disk
                    friday_web::core::Method::Put => friday_web::request_json(
                        r,
                        &|audio| self.set_examples(audio)),
                    m => friday_web::not_acceptable!("Only Put or Get is accepted for 'DDL'\
                        examples endpoint I received: {:?}", m)

                },

                "sensitivity" => match r.method() {
                    friday_web::core::Method::Get => self.get_sensitivity(),     // This gets the commands
                    // This updates the commands and stores updates to disk
                    friday_web::core::Method::Put => friday_web::request_json(
                        r,
                        &|sensitivity_message| self.set_sensitivity(sensitivity_message)),
                    m => friday_web::not_acceptable!("Only Put or Get is accepted for 'DDL'\
                        sensitivity endpoint I received: {:?}", m)
                },

                _ => frierr!("Unknown endpoint name {}", name)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use friday_inference::Model;
    use std::path::PathBuf;
    use std::sync::Mutex;
    use std::env;
    use ureq;

    #[test]
    fn ddl_model() {
        env::set_var("FRIDAY_CONFIG", "test-resources");

        let config = Config {
            audio: [
                ("hello-123.wav".to_owned(), "kalle".to_owned()),
                ("955-184-642-144.wav".to_owned(), "1234".to_owned()),
            ].iter().cloned().collect(),
            export_dir: PathBuf::from("test-resources/ddl_apr_13_eu"),
            sensitivity: 2.0
        };

        let mut model = DDL::model_from_config(config).expect("Failed to load Config");
        friday_logging::info!("Loaded DDL successfully!");


        let v: Vec<i16> = vec![1; 16000];

        let pred: friday_inference::Prediction = model.predict(&v).expect("Failed to predict");

        match pred {
            friday_inference::Prediction::Result {
                class,
            } => assert_eq!(class, String::from("1234")),

            friday_inference::Prediction::Silence => friday_logging::info!("Got Silence"),
            friday_inference::Prediction::Inconclusive => friday_logging::info!("Got Inconclusive")

        }
    }

    #[test]
    fn ddl_web_get_examples_and_sensitivity() {
        env::set_var("FRIDAY_GUI", ".");
        env::set_var("FRIDAY_CONFIG", "test-resources");

        let config = Config {
            audio: [
                ("hello-123.wav".to_owned(), "kalle".to_owned()),
                ("955-184-642-144.wav".to_owned(), "1234".to_owned()),
            ].iter().cloned().collect(),
            export_dir: PathBuf::from("test-resources/ddl_apr_13_eu"),
            sensitivity: 2.0
        };

        let model = DDL::model_from_config(config).expect("Failed to load Config");

        let web = WebDDL::new(&model);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web))
        ]).expect("Failed to register DDL web vendor");
        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(2000));
        let resp = ureq::get(
            "http://0.0.0.0:8000/friday-inference/tensorflow-models/ddl/examples").call();
        let examples = resp.into_json_deserialize::<HashMap<String, String>>()
            .expect("Failed to parse json response");

        friday_logging::info!("Got examples response: {:?}", examples);
        assert_eq!(examples, model.examples.read().unwrap().audio.clone());

        let resp = ureq::get(
            "http://0.0.0.0:8000/friday-inference/tensorflow-models/ddl/sensitivity").call();
        let sensitivity : f32 = resp.into_json_deserialize::<f32>()
            .expect("Failed to parse json response");

        friday_logging::info!("Got sensitivity response: {:?}", sensitivity);
        assert_eq!(sensitivity, model.sensitivity.read().unwrap().clone());


        handle.stop();
    }

    #[test]
    fn ddl_web_set_examples() {
        env::set_var("FRIDAY_GUI", ".");
        env::set_var("FRIDAY_CONFIG", "test-resources");

        let config = Config {
            audio: [
                ("hello-123.wav".to_owned(), "kalle".to_owned()),
            ].iter().cloned().collect(),
            export_dir: PathBuf::from("test-resources/ddl_apr_13_eu"),
            sensitivity: 2.0
        };

        let model = DDL::model_from_config(config.clone()).expect("Failed to load Config");

        let web = WebDDL::new(&model);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web))
        ]).expect("Failed to register DDL web vendor");
        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(2000));
        let resp = ureq::get(
            "http://0.0.0.0:8000/friday-inference/tensorflow-models/ddl/examples").call();
        let examples = resp.into_json_deserialize::<HashMap<String, String>>()
            .expect("Failed to parse json response");

        friday_logging::info!("Got examples response: {:?}", examples);
        assert_eq!(examples, model.examples.read().unwrap().audio.clone());

        let mut update = config.audio.clone();
        update.insert("955-184-642-144.wav".to_owned(), "1234".to_owned());


        let resp = ureq::put("http://0.0.0.0:8000/friday-inference/tensorflow-models/ddl/examples")
            .send_json(serde_json::to_value(update).expect("Failed to serialize state"));

        // Setting examples went fine!
        assert_eq!(resp.status(), 200);

        friday_logging::info!("Examples is now {:?}", model.examples.read().unwrap());

        let mut update = config.audio.clone();
        update.insert("955-184-642-144.wav".to_owned(), "kalle".to_owned());
        *update.get_mut("hello-123.wav").unwrap() = "1234".to_owned();

        let resp = ureq::put("http://0.0.0.0:8000/friday-inference/tensorflow-models/ddl/examples")
            .send_json(serde_json::to_value(update).expect("Failed to serialize state"));

        // Setting examples went fine!
        assert_eq!(resp.status(), 200);

        friday_logging::info!("Examples is now {:?}", model.examples.read().unwrap());


        handle.stop();
    }
}
