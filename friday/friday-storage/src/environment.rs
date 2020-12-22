use std::env;
use friday_error;
use friday_error::frierr;
use friday_error::FridayError;

pub fn get_environment<S: AsRef<str>>(name: S) -> Result<String, FridayError> {
    return env::var(name.as_ref()).or_else(
        |err| frierr!("Unable to get environment variable {} - Reason {}\
        \n\nThings to try\n1. Try setting it to some value {}=..", 
            name.as_ref(), 
            err,
            name.as_ref()));
}
