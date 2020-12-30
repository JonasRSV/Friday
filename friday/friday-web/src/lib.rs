use friday_error::{FridayError, propagate, frierr};
use serde_json;
use serde::Serialize;
use serde::de::DeserializeOwned;


pub mod core;
pub mod server;
pub mod webgui;
pub mod path;
pub mod endpoint;
pub mod vendor;


mod impl_tiny_http;
mod tests;


pub fn get_name(
    r: &mut dyn core::FridayRequest, 
    endpoints: &Vec<endpoint::Endpoint>) -> Result<String, FridayError> {
    let url_str = r.url();
    let url_str_ref = &url_str;
    url::Url::parse(&url_str_ref.clone()).map_or_else(
        |err| frierr!("Failed to parse url {} - Reason: {}", url_str_ref.clone(), err),
        |u| endpoint::Endpoint::match_on_path(u.path(), endpoints).map_or_else(
            propagate!("Failed to get endpoint for {}", url_str_ref.clone()),
            |name| Ok(name.to_owned())
        ))
}

pub fn response_forbidden<S: AsRef<str>>(message: S) -> Result<core::Response, FridayError> {
    Ok(core::Response::TEXT { status: 405, content: String::from(message.as_ref()) })
}

#[macro_export]
macro_rules! forbidden {
    ($str:expr $(,$arg: expr)*) => {
        $crate::response_forbidden(format!($str $(,$arg)*)).into()
    }
}

pub fn response_not_acceptable<S: AsRef<str>>(message: S) -> Result<core::Response, FridayError> {
    Ok(core::Response::TEXT { status: 406, content: String::from(message.as_ref()) })
}

#[macro_export]
macro_rules! not_acceptable {
    ($str:expr $(,$arg: expr)*) => {
        $crate::response_not_acceptable(format!($str $(,$arg)*)).into()
    }
}

pub fn response_ok<S: AsRef<str>>(message: S) -> core::Response {
    let owned_message = message.as_ref().to_owned();
    core::Response::JSON {
        status: 200, 
        content: serde_json::json!({
            "ok": true,
            "message": owned_message
        }).to_string()
    }
}

#[macro_export]
macro_rules! ok {
    ($str:expr $(,$arg: expr)*) => {
        $crate::response_ok(format!($str $(,$arg)*)).into()
    }
}

pub fn response_not_ok<S: AsRef<str>>(message: S) -> core::Response {
    let owned_message = message.as_ref().to_owned();
    core::Response::JSON {
        status: 200, 
        content: serde_json::json!({
            "ok": false,
            "message": owned_message
        }).to_string()
    }
}


#[macro_export]
macro_rules! not_ok {
    ($str:expr $(,$arg: expr)*) => {
        $crate::response_not_ok(format!($str $(,$arg)*)).into()
    }
}

pub fn response_json<S>(status: i32, value: &S) -> Result<core::Response, FridayError> 
where S: Serialize {
    serde_json::to_string(value).map_or_else(
        |err| frierr!("Failed to serialize JSON response - Reason: {}", err),
        |content| Ok(core::Response::JSON{ status, content}))
}

#[macro_export]
macro_rules! json {
    ($status:expr, $obj:expr) => {
        $crate::response_json($status, $obj).into()
    }
}


impl<T> Into<Result<core::Response, T>> for core::Response {
    fn into(self) -> Result<core::Response, T> {
        return Ok(self);
    }
}

pub fn request_json<S>(
    r: &mut dyn core::FridayRequest, 
    f: &dyn Fn(S) -> Result<core::Response, FridayError>) -> Result<core::Response, FridayError> 
    where S: DeserializeOwned {
        match r.data() {
            Ok(data) => match data { 
                    core::Data::JSON { json } => 
                                    serde_json::from_str(&json).map_or_else(
                                        |err| frierr!(
                                            "Failed to deserialize JSON body - Reason : {}\n\
                                            BODY: {}", err, json),
                                            f),
            _ => not_acceptable!("Body must contain JSON data"),

            },
            Err(err) => propagate!("Unable to get data from request")(err)
    }
}
