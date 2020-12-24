use friday_error::FridayError;
use friday_error::propagate;
use friday_error::frierr;


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

pub fn not_acceptable<S: AsRef<str>>(message: S) -> Result<core::Response, FridayError> {
    Ok(core::Response::TEXT { status: 406, content: String::from(message.as_ref()) })
}
