use url;
use crate::core::{Vendor, Response, EndPoint, FridayRequest};
use friday_error::FridayError;
use friday_error::frierr;
use friday_error::propagate;
use friday_storage::environment;
use std::fs::File;
use std::path::Path;
use std::ffi::OsStr;


pub struct WebGui {
    pub root: String
}

impl WebGui {
    pub fn new() -> Result<WebGui, FridayError> {
        return environment::get_environment("FRIDAY_WEB_GUI").map_or_else(
            propagate!("Failed to get WEB_GUI directory"),
            |dir| Ok(WebGui {
                root: dir
            }));

    }
}

fn get_path_relative_to_static(u: String) -> Result<String, FridayError>  {
    return url::Url::parse(&u).map_or_else(
        |err| frierr!("Failed to parse url {} - Reason: {}", u, err),
        |u| {
            let mut iter = u.path().split("/");

            // Drop empty "" before first /
            iter.next();

            // This makes it so that
            // www.hello.com and www.hello.com/ both returns homepage
            return match iter.next() {
                Some(path) => match path {
                    "static" => Ok(iter.fold(String::from("/static"), |acc, elem| acc + "/" + elem)),
                    "" => Ok("/index.html".to_owned()), // Also homepage.. 
                    _ => frierr!("Root path must be static - Found {}", path)
                }
                None =>  Ok("/index.html".to_owned()) // Return homepage.. 
            }
        });
}

fn file_extension(file_path: &str) -> Option<&str> {
    Path::new(file_path)
        .extension()
        .and_then(OsStr::to_str)
}

fn infer_content_type(file_path: String, _: &File) -> Result<String, FridayError> {
    // TODO: Maybe in future we can try to infer content time from looking at file header in file
    // too?
    return file_extension(file_path.as_str()).map_or_else(
        || frierr!("Could not fine file extension for {}", file_path),
        |extension| match extension {
        "html" => Ok("text/html".to_owned()),
        "htm" => Ok("text/html".to_owned()),
        "css" => Ok("text/css".to_owned()),
        "js" => Ok("text/javascript".to_owned()),
        "png" => Ok("image/png".to_owned()),
        "jpg" => Ok("image/jpeg".to_owned()),
        "svg" => Ok("image/svg+xml".to_owned()),
        _ => frierr!("Unknown content type for {}", file_path)
    });
}

impl Vendor for WebGui {
    fn name(&self) -> String { return String::from("WebGui"); }
    // This is a special vendor so no need to specify any endpoints
    fn endpoints(&self) -> Vec<EndPoint> { return Vec::new(); }
    fn handle(&mut self, r: &mut dyn FridayRequest) 
        -> Result<Response, FridayError> {
            return get_path_relative_to_static(r.url()).map_or_else(
               propagate!("Could not parse relative path from URL"),
                    // TODO: this might be a security issue since clients can ../ to get parent files
               |rel| File::open(self.root.clone() + &rel).map_or_else(
                   |err| frierr!("Failed to open file {} - Reason: {}", self.root.clone() + &rel, err),
                   |file| infer_content_type(self.root.clone() + &rel, &file).map_or_else(
                       propagate!("Failed to infer content type"),
                       |content_type| Ok( Response::FILE { status: 200, file, content_type })
               )));
    }
}

#[cfg(test)]
mod tests {
    use crate::server::*;
    use std::env;

    #[test]
    fn serve_webgui() {
        env::set_var("FRIDAY_WEB_GUI", ".");
        let mut server = Server::new().expect("Failed to create server");
        let handles = server.listen("0.0.0.0:8000").expect("Failed to launch server");

        for handle in handles {
            handle.join().expect("Failed to join thread");
        }
    }
}
