use std::{fmt::Debug, collections::VecDeque};

#[derive(Clone)]
pub struct FridayError{
    trace: VecDeque<String>
}

impl FridayError {
    pub fn new(message: &str) -> FridayError {
        let mut trace = VecDeque::new();
        trace.push_back(String::from(message.clone()));

        return FridayError{
            trace
        }
    }

    pub fn from(message: String) -> FridayError {
        let mut trace = VecDeque::new();
        trace.push_back(message);

        return FridayError{
            trace
        }

    }

    pub fn len(&self) -> usize {
        return self.trace.len();
    }

    pub fn push<S>(&self, message: S) -> FridayError
        where S: AsRef<str>{
            let mut clone = self.clone();
            clone.trace.push_back(String::from(message.as_ref()));
            return clone;
    }

    pub fn propagate<T>(message: &str, r: Result<T, FridayError>) -> Result<T, FridayError> {
        match r {
            Ok(r) => Ok(r),
            Err(mut err) => {
                err.trace.push_back(String::from(message));
                return Err(err);
            }
        }

    }
}

impl Debug for FridayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("\n").unwrap();
        f.write_str("\n").unwrap();
        f.write_str("--- Friday Error --- \n").unwrap();
        f.write_str("\n").unwrap();
        f.write_str("\n").unwrap();
        for entry in self.trace.iter().rev() {

            f.write_str(&entry).unwrap();
            f.write_str("\n\n").unwrap();
        }

        f.write_str("\n").unwrap();
        f.write_str("\n").unwrap();
        f.write_str("--- End --- \n").unwrap();
        return Ok(())
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
