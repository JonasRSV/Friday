use crate::model as m;
use crate::config as c;
use std::ffi::CString;
use float_ord::FloatOrd;
use inference;


pub struct Discriminative {
    model: m::Model,
    input: m::Tensor,
    output: m::Tensor,
    class_map: Vec<String>

}

impl Discriminative {

    pub fn new() -> Discriminative {
        let config = c::Discriminative::new();
        return Discriminative::model_from_config(config);
    }

    fn model_from_config(config: c::Discriminative) -> Discriminative {
        let model = m::Model::new(config.export_dir.as_path())
            .expect("(tensorflow-models): Failed to initialize model");

        let input_cstring = CString::new("input")
            .expect("(tensorflow-models):  Failed to create cstring out of input_op_name");

        let output_cstring = CString::new("output")
            .expect("(tensorflow-models): Failed to create cstring out of output_op_name");

        let input_tensor = m::Tensor::new(&model, &input_cstring);
        let output_tensor = m::Tensor::new(&model, &output_cstring);

        let output_dim = output_tensor
            .dims
            .first()
            .expect("(tensorflow-models): Failed to read first dim of output tensor")
            .clone() as usize;

        if output_dim != config.class_map.len() {
            panic!("Class map size ({}) not matching output dimension of tensor ({})", 
                config.class_map.len(), output_dim);

        }

        return Discriminative {
            model,
            input: input_tensor,
            output: output_tensor,
            class_map: config.class_map.clone()
        }

    }
}

impl inference::Model for Discriminative {
    fn predict(&mut self, v :&Vec<i16>) -> inference::Prediciton {
        //println!("Predicting..!");
        self.input.set_data(&v);
        self.model.run(&mut self.input, &mut self.output);
        let probabilities = self.output.get_data::<f32>();

        println!("Probabilities {:?}", probabilities);
        let pred = probabilities
            .iter()
            .enumerate()
            .max_by_key(|k| FloatOrd(k.1.clone()))
            .map(|k| k.0)
            .expect("failed to get max").clone();

        return inference::Prediciton {
            class: self.class_map[pred].clone()
        }
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
                String::from("?")]
        };

        let mut model = Discriminative::model_from_config(config);
        let v: Vec<i16> = vec![1; 16000];

        let pred: inference::Prediciton = model.predict(&v);

        assert_eq!(pred.class, String::from("Silence"));
    }
}
