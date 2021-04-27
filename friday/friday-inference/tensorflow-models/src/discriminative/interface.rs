use crate::discriminative::model as m;
use std::ffi::CString;
use float_ord::FloatOrd;

use friday_inference;

use friday_error::{frierr, propagate, FridayError};
use friday_logging;

use friday_storage;
use friday_web;

use std::path::PathBuf;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use serde_derive::Deserialize;
use serde_json;


#[derive(Deserialize)]
pub struct Config {
    export_dir: PathBuf,
    sensitivity: f32,
    class_map: HashMap<String, i32>
}

pub struct Discriminative {
    model: m::Model,
    input: m::Tensor,
    output: m::Tensor,
    class_map: Arc<RwLock<Vec<String>>>,
    sensitivity: Arc<RwLock<f32>>

}

fn class_map_to_class_vec(map: HashMap<String, i32>) -> Vec<String> {
    // TODO is there a better way to convert it
    // We just want to take a map
    // "hi: 0
    // "why": 1
    // "who": 2
    // ...
    // and convert into
    // ["hi", "why", "who"]
    // Such that the order is preserved

    let mut class_map_mappings_vec: Vec<(String, i32)> = map
        .iter()
        .map(|k| (k.0.clone(), k.1.clone()))
        .collect();

    class_map_mappings_vec.sort_by_key(|k| k.1);

    // Finally we have the class_map
    return class_map_mappings_vec.iter().map(|k| k.0.clone()).collect();
}

impl Discriminative {

    pub fn new() -> Result<Discriminative, FridayError>  {
        return friday_storage::config::get_config("discriminative.json").map_or_else(
            propagate!("Failed to create discriminative model"),
            Discriminative::model_from_config 
        );
    }
    fn model_from_config(config: Config) ->
        Result<Discriminative, FridayError> {
            let maybe_input = CString::new("input");
            let maybe_output = CString::new("output");
            let class_map : Vec<String> = class_map_to_class_vec(config.class_map.clone());


            return m::Model::new(config.export_dir.as_path())
                .map_or_else(
                    || frierr!("Failed to create model"),
                    |model|  Discriminative::make_discriminative(
                        class_map, 
                        config.sensitivity,
                        model,
                        maybe_input.unwrap(),
                        maybe_output.unwrap()));
    }

    fn make_discriminative(class_map: Vec<String>,
        sensitivity: f32,
        m: m::Model, 
        input_cstring: CString,
        output_cstring: CString) -> Result<Discriminative, FridayError> {

        let input_tensor = m::Tensor::new(&m, &input_cstring);
        let output_tensor = m::Tensor::new(&m, &output_cstring);

        output_tensor
            .dims
            .clone()
            .first()
            .map_or_else(
                || frierr!("Failed to read dimension of output tensor"),
                |dim| {

                    if dim.clone() as usize != class_map.len() {
                        return frierr!("Class map size ({}) \
                        not matching output dimension of tensor ({})", 
                        class_map.len(), dim);

                    } 
                    return Ok(Discriminative {
                        model: m,
                        input: input_tensor,
                        output: output_tensor,
                        // Storing this behind a lock because the WebDiscriminativemight read it
                        // in another thread.
                        class_map: Arc::new(RwLock::new(class_map.clone())), 
                        sensitivity: Arc::new(RwLock::new(sensitivity))
                    });

                })
    }



}

impl friday_inference::Model for Discriminative {
    fn predict(&mut self, v :&Vec<i16>) -> Result<friday_inference::Prediction, FridayError> {

        match self.class_map.read() {
            Ok(class_map) => match self.sensitivity.read() {
                Ok(sensitivity) => {
                    self.input.set_data(&v);
                    self.model.run(&mut self.input, &mut self.output);
                    let probabilities = self.output.get_data::<f32>();

                    let pred = probabilities
                        .iter()
                        .enumerate()
                        .max_by_key(|k| FloatOrd(k.1.clone()))
                        .map(|k| k.0)
                        .expect("failed to get max").clone();

                    friday_logging::info!("P({}) = {}", class_map[pred], probabilities[pred]);

                    if pred == 0 {
                        return Ok(friday_inference::Prediction::Silence);
                    }

                    if probabilities[pred] > sensitivity.clone() {
                        return Ok(friday_inference::Prediction::Result {
                            class: class_map[pred].clone(),
                        })
                    }

                    return Ok(friday_inference::Prediction::Inconclusive);

                },
                Err(err) => frierr!("Failed to read RWLocked sensitivity - Reason: {}", err)

            },
            Err(err) => frierr!("Failed to read RWLocked class_map - Reason: {}", err)

        }

    }

    fn expected_frame_size(&self) -> usize {
        return self.input
            .dims
            .first()
            .expect("(tensorflow-models): Failed to extract input dims from model")
            .clone() as usize;
    }

    fn reset(&mut self) -> Result<(), FridayError> {
        Ok(())
    }
}

pub struct WebDiscriminative{
    endpoints: Vec<friday_web::endpoint::Endpoint>,

    // These are shared with the Discriminative
    class_map: Arc<RwLock<Vec<String>>>,
    sensitivity: Arc<RwLock<f32>>
}

impl WebDiscriminative{
    pub fn new(d: &Discriminative) -> WebDiscriminative{
        WebDiscriminative{
            endpoints: vec![
                friday_web::endpoint::Endpoint{ 
                    name: "classes".to_owned(),
                    methods: vec![friday_web::core::Method::Get],
                    path: friday_web::path::Path::safe_new(
                        "/friday-inference/tensorflow-models/discriminative/classes")
                },
                friday_web::endpoint::Endpoint{ 
                    name: "sensitivity".to_owned(),
                    methods: vec![friday_web::core::Method::Get],
                    path: friday_web::path::Path::safe_new(
                        "/friday-inference/tensorflow-models/discriminative/sensitivity")
                }
            ],
            class_map: d.class_map.clone(),
            sensitivity: d.sensitivity.clone()
        }
    }

    fn class_map_response(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.class_map.read() {
            Ok(class_map) => serde_json::to_string(&class_map.clone()).map_or_else(
                |err| frierr!(
                    "Failed to serialize class_map - {:?} - to json - Reason: {}", 
                    class_map, 
                    err),
                    |content|  Ok(friday_web::core::Response::JSON {
                        status: 200, content 
                    })),

            Err(err) => frierr!("Failed to read RWLocked class_map - Reason: {}", err)
        }
    }

    fn sensitivity_response(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.sensitivity.read() {
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

}

impl friday_web::vendor::Vendor for WebDiscriminative{
    fn name(&self) -> String { return "friday-inference/tensorflow-models/discriminative".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> Result<friday_web::core::Response, FridayError> {
        friday_web::get_name(r, &self.endpoints).map_or_else(
            propagate!("Failed to get 'Discriminiative' endpoint for {}", r.url()),
            |name| match name.as_str() {
                "classes" => self.class_map_response(),
                "sensitivity" => self.sensitivity_response(),
                _ => frierr!("Unknown endpoint name {}", name)
            })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use friday_inference::Model;
    use std::path::PathBuf;
    use std::sync::Mutex;
    use ureq;

    #[test]
    fn discriminative_model() {

        let config = Config {
            export_dir: PathBuf::from("test-resources/1603634879"),
            class_map: [
                (String::from("Silence"), 0), 
                (String::from("a"), 1),
                (String::from("b"), 2),
                (String::from("c"), 3),
                (String::from("d"), 4),
                (String::from("e"), 5),
                (String::from("f"), 6),
                (String::from("g"), 7),
                (String::from("h"), 8),
                (String::from("i"), 9)].iter().cloned().collect(),
                sensitivity: 0.0
        };

        let mut model = Discriminative::model_from_config(config).expect("Failed to load Config");
        let v: Vec<i16> = vec![1; 16000];

        let pred: friday_inference::Prediction = model.predict(&v).expect("Failed to predict");

        match pred {
            friday_inference::Prediction::Result {
                class,
            } => assert_eq!(class, String::from("Silence")),

            friday_inference::Prediction::Silence => friday_logging::info!("Got Silence"),
            friday_inference::Prediction::Inconclusive => friday_logging::info!("Got Inconclusive")

        }
    }
    use std::env;

    #[test]
    fn discriminative_web() {
        env::set_var("FRIDAY_GUI", ".");

        let config = Config {
            export_dir: PathBuf::from("test-resources/1603634879"),
            class_map: [
                (String::from("Silence"), 0), 
                (String::from("a"), 1),
                (String::from("b"), 2),
                (String::from("c"), 3),
                (String::from("d"), 4),
                (String::from("e"), 5),
                (String::from("f"), 6),
                (String::from("g"), 7),
                (String::from("h"), 8),
                (String::from("i"), 9)].iter().cloned().collect(),
                sensitivity: 0.0
        };

        let model = Discriminative::model_from_config(config).expect("Failed to load Config");

        let web = WebDiscriminative::new(&model);

        let mut server = friday_web::server::Server::new().expect("Failed to create web friday server");
        server.register(vec![
            Arc::new(Mutex::new(web))
        ]).expect("Failed to register discriminative web vendor");
        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(2000));
        let resp = ureq::get(
            "http://0.0.0.0:8000/friday-inference/tensorflow-models/discriminative/classes").call();
        let class_map : Vec<String> = resp.into_json_deserialize::<Vec<String>>()
            .expect("Failed to parse json response");

        friday_logging::info!("Got class_map response: {:?}", class_map);
        assert_eq!(class_map, model.class_map.read().unwrap().clone());

        let resp = ureq::get(
            "http://0.0.0.0:8000/friday-inference/tensorflow-models/discriminative/sensitivity").call();
        let sensitivity : f32 = resp.into_json_deserialize::<f32>()
            .expect("Failed to parse json response");

        friday_logging::info!("Got sensitivity response: {:?}", sensitivity);
        assert_eq!(sensitivity, model.sensitivity.read().unwrap().clone());


        handle.stop();
    }
}
