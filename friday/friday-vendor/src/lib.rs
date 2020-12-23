use friday_error::FridayError;

pub enum DispatchResponse {
    Success,
    NoMatch,
}

pub trait Vendor {
    fn name(&self) -> String;
    fn dispatch(&self, action : &String) -> Result<DispatchResponse, FridayError>;
}

pub struct DummyVendor;

impl DummyVendor {
    pub fn new() -> DummyVendor {
        return DummyVendor{};
    }
}

impl Vendor for DummyVendor {
    fn name(&self) -> String { "Dummy".to_owned() }
    fn dispatch(&self, action : &String) -> Result<DispatchResponse, FridayError> {
        println!("Dummy received {}", action);

        return Ok(DispatchResponse::Success);
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        let dummy = DummyVendor::new();
        let message = String::from("hello");
        match dummy.dispatch(&message).unwrap() {
            DispatchResponse::Success => println!("Success!"),
            DispatchResponse::NoMatch => eprintln!("No match"),
        }
    }
}
