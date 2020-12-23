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

