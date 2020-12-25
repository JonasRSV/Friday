use crate::core::{Response, FridayRequest, Method};
use crate::vendor::Vendor;
use crate::endpoint::Endpoint;
use friday_error::FridayError;
use friday_error::frierr;
use friday_error::propagate;
use friday_storage::environment;
use std::fs::File;
use std::path::Path;
use std::ffi::OsStr;
use crate::path;
use url;


pub struct WebGui {
    pub root: String,
    endpoints: Vec<Endpoint>
}

impl WebGui {
    pub fn new() -> Result<WebGui, FridayError> {
        return environment::get_environment("FRIDAY_WEB_GUI").map_or_else(
            propagate!("Failed to get WEB_GUI directory"),
            |dir| Ok(WebGui {
                root: dir,
                endpoints: vec![
                    Endpoint{ 
                        name: "static".to_owned(),
                        methods: vec![Method::Get],
                        path: path::Path::safe_new(format!("/static/{}", path::Symbol::Own))
                    },
                    Endpoint{ 
                        name: "home".to_owned(),
                        methods: vec![Method::Get],
                        path: path::Path::safe_new("/")
                    },
                    Endpoint{ 
                        name: "index".to_owned(),
                        methods: vec![Method::Get],
                        path: path::Path::safe_new("/index.html")
                    }
                ]

            }));

    }

    fn homepage(&self) -> Result<Response, FridayError> {
        let index = self.root.clone() + "/index.html";
        File::open(index.clone()).map_or_else(
            |err| frierr!("Failed to open file {} - Reason: {}", index, err),
            |file| Ok( Response::FILE { status: 200, file, content_type: "text/html".to_owned() }))
    }

    fn serve(&self, path: String) -> Result<Response, FridayError> {
        let file_name = self.root.clone() + path.as_str();
        let file_name_ref = &file_name;

        File::open(file_name.clone()).map_or_else(
            |err| frierr!("Failed to open file {} - Reason: {}", file_name_ref.clone(), err),
            |file| infer_content_type(file_name_ref.clone(), &file).map_or_else(
                propagate!("Failed to infer content type"),
                |content_type| Ok( Response::FILE { status: 200, file, content_type })
            ))

    }
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
    fn endpoints(&self) -> Vec<Endpoint> { 
        return self.endpoints.clone();
    }

    fn handle(&mut self, r: &mut dyn FridayRequest) 
        -> Result<Response, FridayError> {
            let url_str = r.url();
            let url_str_ref = &url_str;
            url::Url::parse(&url_str_ref.clone()).map_or_else(
                |err| frierr!("Failed to parse url {} - Reason: {}", url_str_ref.clone(), err),
                |u| Endpoint::match_on_path(u.path(), &self.endpoints).map_or_else(
                    propagate!("Failed to get 'WebGui' endpoint for {}", url_str_ref.clone()),
                    |name| match name {
                        "static" => match path::rel_from(u.path(), "static") {
                            // TODO: this should never occur.. can we get rid of this check?
                            None => frierr!("Ops.. Unable to find 'static' in url {}", url_str_ref.clone()),
                            Some(rel) => self.serve("/static".to_owned() + rel.as_str())

                        },
                        "home" => self.homepage(),
                        "index" => self.homepage(),
                        _ => frierr!("Unknown endpoint {}", name)
                    }))
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
        let handle = server.listen("0.0.0.0:8000").expect("Failed to launch server");

        handle.wait();
    }
}
