use friday_error::FridayError;
use std::fs::File;

pub enum Response {
    Empty{status: i32},
    JSON {status: i32, content: String},
    TEXT {status: i32, content: String},
    FILE {status: i32, file: File, content_type: String }
}

#[derive(Clone, PartialEq)]
pub enum Method {
    Get,
    Post,
    Put,
    Patch,
    Head,
    Delete,
    Connect,
    Trace,
    Options,
    Unknown
}

pub struct EndPoint {
    pub methods: Vec<Method>,
    pub path: String
}

pub enum Data {
    Empty,
    JSON {json: String},
    TEXT {text: String}
}


pub trait FridayRequest {
    fn method(&self) -> Method;
    fn data(&mut self) -> Result<Data, FridayError>;
    fn url(&self) -> String;
}

pub trait Vendor {
    fn name(&self) -> String;
    fn endpoints(&self) -> Vec<EndPoint>;
    fn handle(&mut self, r: &mut dyn FridayRequest) -> Result<Response, FridayError>;
}
