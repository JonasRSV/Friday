use friday_error::FridayError;

#[derive(Debug, Clone)]
pub enum Prediction {
    Result {
        class: String,
    },
    Silence,
    Inconclusive

}

pub trait Model {

    fn reset(&mut self) -> Result<(), FridayError>;
    fn predict(&mut self, v :&Vec<i16>) -> Result<Prediction, FridayError>;
    fn expected_frame_size(&self) -> usize;
}

pub struct DummyModel {
    ret: Prediction
}

impl DummyModel {
    pub fn new(c: String) -> DummyModel {
        return DummyModel{
            ret: Prediction::Result {
                class: c,
            }
        }
    }
}

impl Model for DummyModel {
    fn predict(&mut self, _ :&Vec<i16>) -> Result<Prediction, FridayError> {
        return Ok(self.ret.clone());
    }

    fn expected_frame_size(&self) -> usize {
        return 16000;
    }

    fn reset(&mut self) -> Result<(), FridayError> {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn try_dummy() {
        let mut dummy = DummyModel::new(String::from("Hello"));

        let v: Vec<i16> = vec![0];
        assert_eq!(dummy.predict(&v).unwrap().class, String::from("Hello"));
    }
}
