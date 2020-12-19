use crate::model as m;
use std::ffi::CString;
use float_ord::FloatOrd;
use inference;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;

use friday_storage;

use std::path::PathBuf;
use std::collections::HashMap;
use serde_derive::Deserialize;

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
    class_map: Vec<String>,
    sensitivity: f32

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
            friday_error::propagate("Failed to create discriminative model"),
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
                        class_map: class_map.clone(),
                        sensitivity
                    });

                })
    }



}

impl inference::Model for Discriminative {
    fn predict(&mut self, v :&Vec<i16>) -> inference::Prediction {
        //println!("Predicting..!");
        self.input.set_data(&v);
        self.model.run(&mut self.input, &mut self.output);
        let probabilities = self.output.get_data::<f32>();

        let pred = probabilities
            .iter()
            .enumerate()
            .max_by_key(|k| FloatOrd(k.1.clone()))
            .map(|k| k.0)
            .expect("failed to get max").clone();

        println!("P({}) = {}", self.class_map[pred], probabilities[pred]);

        if pred == 0 {
            return inference::Prediction::Silence;
        }

        if probabilities[pred] > self.sensitivity {
            return inference::Prediction::Result {
                class: self.class_map[pred].clone(),
                index: pred as u32
            }
        }

        return inference::Prediction::Inconclusive;

    }

    fn expected_frame_size(&self) -> usize {
        return self.input
            .dims
            .first()
            .expect("(tensorflow-models): Failed to extract input dims from model")
            .clone() as usize;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use inference::Model;
    use std::path::PathBuf;
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

        let pred: inference::Prediction = model.predict(&v);

        match pred {
            inference::Prediction::Result {
                class,
                index: _
            } => assert_eq!(class, String::from("Silence")),

            inference::Prediction::Silence => eprintln!("Got Silence"),
            inference::Prediction::Inconclusive => eprintln!("Got Inconclusive")

        }

    }
}
