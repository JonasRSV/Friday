use tiny_http;
use crate::core::{Method, Data, FridayRequest};
use friday_error::FridayError;
use friday_error::frierr;

fn get_content_type(r : &tiny_http::Request) -> Option<String> {
    return match r.headers().iter().position(
        |header| header.field.to_string() == "Content-Type") {
        Some(index) => Some(r.headers()[index].value.to_string()),
        None => None
    }
}

fn utf8_to_string(bytes: &Vec<u8>) -> String {
    return String::from_utf8_lossy(bytes.as_slice()).to_string();
}

fn utf16_to_string(bytes: &Vec<u8>) -> String {
    // This is a safe conversion.. but requires some extra copying
    // If this is a bottleneck we can do unsafe by converting to raw pointer and casting to short.
    let bytes: Vec<u16> = bytes
        .chunks_exact(2)
        .into_iter()
        .map(|a| u16::from_ne_bytes([a[0], a[1]]))
        .collect();
    return String::from_utf16_lossy(bytes.as_slice()).to_string();
}

impl FridayRequest for tiny_http::Request {
    fn method(&self) -> Method {
        match self.method() {
            tiny_http::Method::Get => Method::Get,
            tiny_http::Method::Post => Method::Post,
            tiny_http::Method::Put => Method::Put,
            tiny_http::Method::Patch => Method::Patch,
            tiny_http::Method::Head => Method::Head,
            tiny_http::Method::Delete => Method::Delete,
            tiny_http::Method::Connect => Method::Connect,
            tiny_http::Method::Trace => Method::Trace,
            tiny_http::Method::Options => Method::Options,
            tiny_http::Method::NonStandard{0:_} => Method::Unknown
        }
    }


    fn data(&mut self) -> Result<Data, FridayError> {
        let mut content = Vec::new();
        return self.as_reader().read_to_end(&mut content).map_or_else(
            |err| frierr!("Failed to read data from http request - Reason: {}", err),
            |_| match get_content_type(self) {
                None => frierr!("Error: Request did not contain a Content-Type header"),
                Some(content_type) => match content_type.as_str() {
                    "text/plain" => Ok( Data::TEXT { text: utf8_to_string(&content) }),
                    "text/plain; charset=utf8" => Ok( Data::TEXT { text: utf8_to_string(&content) }),
                    "text/plain; charset=utf16" => Ok( Data::TEXT { text: utf16_to_string(&content) }),
                    "application/json" => Ok( Data::JSON { json: utf8_to_string(&content) }),
                    "application/json; charset=utf8" => Ok( Data::JSON { json: utf8_to_string(&content) }),
                    "application/json; charset=utf16" => Ok( Data::JSON { json: utf16_to_string(&content) }),
                    _ => frierr!("Unknown Content-Type {}", content_type)

                }

            }

        );
    }

    fn url(&self) -> String {
        return String::from(format!("http://{}{}", self.remote_addr(), self.url()));
    }
}
