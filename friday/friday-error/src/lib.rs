use std::{fmt::Debug, collections::VecDeque};

#[derive(Clone)]
pub struct FridayError{
    trace: VecDeque<String>
}

#[macro_export]
macro_rules! frierr {
    ($str:expr $(,$arg: expr)*) => {
        FridayError::new(format!($str $(,$arg)*)).into();
    }
}

impl FridayError {
    pub fn new<S>(message: S) -> FridayError 
        where S: AsRef<str> {
            let mut trace = VecDeque::new();
            trace.push_back(String::from(message.as_ref()));

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

impl<T> Into<Result<T, FridayError>> for FridayError {
    fn into(self) -> Result<T, FridayError> {
        return Err(self);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frierr_macro() {
        let f: FridayError = frierr!("Hello {} {} {}", "What", "Are you", "Doing");
        println!("{:?}", f.trace);
        assert_eq!(2 + 2, 4);
    }
}