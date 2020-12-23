use crate::endpoint::Endpoint;
use crate::core::{FridayRequest, Response};
use friday_error::FridayError;

pub trait Vendor {
    fn name(&self) -> String;
    fn endpoints(&self) -> Vec<Endpoint>;
    fn handle(&mut self, r: &mut dyn FridayRequest) -> Result<Response, FridayError>;
}
