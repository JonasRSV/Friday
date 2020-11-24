pub trait Vendor {
    fn dispatch(&self, action : &str) -> Result<(), String>;
}

pub struct DummyVendor;

impl DummyVendor {
    pub fn new() -> DummyVendor {
        return DummyVendor{};
    }
}

impl Vendor for DummyVendor {
    fn dispatch(&self, action : &str) -> Result<(), String> {
        println!("Dummy received {}", action);

        return Ok(());
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        let dummy = DummyVendor::new();
        dummy.dispatch("hello").expect("Dispatch for dummy failed somehow?");
        assert_eq!(2 + 2, 4);
    }
}
