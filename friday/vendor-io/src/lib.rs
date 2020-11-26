use friday_error::FridayError;

pub enum DispatchResponse {
    Success,
    NoMatch,
    Err{err: FridayError}
}

pub trait Vendor {
    fn dispatch(&self, action : &String) -> DispatchResponse;
}

pub struct DummyVendor;

impl DummyVendor {
    pub fn new() -> DummyVendor {
        return DummyVendor{};
    }
}

impl Vendor for DummyVendor {
    fn dispatch(&self, action : &String) -> DispatchResponse {
        println!("Dummy received {}", action);

        return DispatchResponse::Success;
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        let dummy = DummyVendor::new();
        let message = String::from("hello");
        match dummy.dispatch(&message) {
            DispatchResponse::Success => println!("Success!"),
            DispatchResponse::NoMatch => eprintln!("No match"),
            DispatchResponse::Err{err} => eprintln!("err {}", err),
        }
    }
}
