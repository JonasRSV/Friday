
#[derive(Debug, Clone)]
pub struct Prediciton {
    pub class: String
}

pub trait Model {
    fn predict(&mut self, v :&Vec<i16>) -> Prediciton;
    fn expected_frame_size(&self) -> usize;
}

pub struct DummyModel {
    ret: Prediciton
}

impl DummyModel {
    pub fn new(c: String) -> DummyModel {
        return DummyModel{
            ret: Prediciton {
                class: c
            }
        }
    }
}

impl Model for DummyModel {
    fn predict(&mut self, _ :&Vec<i16>) -> Prediciton {
        return self.ret.clone();
    }

    fn expected_frame_size(&self) -> usize {
        return 16000;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn try_dummy() {
        let mut dummy = DummyModel::new(String::from("Hello"));

        let v: Vec<i16> = vec![0];
        assert_eq!(dummy.predict(&v).class, String::from("Hello"));
    }
}
