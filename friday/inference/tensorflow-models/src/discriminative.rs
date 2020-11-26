use crate::model as m;
use crate::config as c;
use std::ffi::CString;
use float_ord::FloatOrd;
use inference;
use friday_error;


pub struct Discriminative {
    model: m::Model,
    input: m::Tensor,
    output: m::Tensor,
    class_map: Vec<String>,
    sensitivity: f32

}

impl Discriminative {

    pub fn new() -> Result<Discriminative, friday_error::FridayError>  {
        match c::Discriminative::new() {
            Ok(config) => Discriminative::model_from_config(config),
            Err(e) => Err(e)
        }
    }

    fn make_discriminative(
        config: c::Discriminative,
        m: m::Model, 
        input_cstring: CString,
        output_cstring: CString) -> Result<Discriminative, friday_error::FridayError> {

        let input_tensor = m::Tensor::new(&m, &input_cstring);
        let output_tensor = m::Tensor::new(&m, &output_cstring);

        output_tensor
            .dims
            .clone()
            .first()
            .map_or_else(
                || Err(friday_error::FridayError::new("Failed to read dimension of output tensor")),
                |dim| {

                    if dim.clone() as usize != config.class_map.len() {
                        return Err(friday_error::FridayError::from(
                                format!("Class map size ({}) \
                        not matching output dimension of tensor ({})", 
                        config.class_map.len(), dim)));

                    } 
                    return Ok(Discriminative {
                        model: m,
                        input: input_tensor,
                        output: output_tensor,
                        class_map: config.class_map.clone(),
                        sensitivity: config.sensitivity as f32
                    });

                })
    }


    fn model_from_config(config: c::Discriminative) ->
        Result<Discriminative, friday_error::FridayError> {

            return m::Model::new(config.export_dir.as_path())
                .map_or_else(
                    || Err(friday_error::FridayError::new("Failed to create model")),
                    |model| {
                        CString::new("input").map_or_else(
                            |_| Err(friday_error::FridayError::new("Failed to create cstring from 'input'")),
                            |input| {
                                CString::new("output").map_or_else(
                                    |_| Err(friday_error::FridayError::new("Failed to create cstring from 'input'")),
                                    |output| Discriminative::make_discriminative(config, model, input, output)
                                )
                            }
                        )
                    }
                );
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

        let config = c::Discriminative {
            export_dir: PathBuf::from("test-resources/1603634879"),
            class_map: vec![
                String::from("Silence"), 
                String::from("?"), 
                String::from("?"), 
                String::from("?"),
                String::from("?"), 
                String::from("?"), 
                String::from("?"),
                String::from("?"), 
                String::from("?"), 
                String::from("?")],
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
