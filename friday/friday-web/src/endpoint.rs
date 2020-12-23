use crate::path;
use crate::core::Method;
use friday_error::frierr;
use friday_error::propagate;
use friday_error::FridayError;

#[derive(Clone)]
pub struct Endpoint {
    pub name: String,
    pub methods: Vec<Method>,
    pub path: path::Path
}

impl Endpoint {

    pub fn match_on_path<S: AsRef<str>>(u: S, endpoints: &Vec<Endpoint>) -> Result<&str, FridayError> {
        return path::Path::new(u.as_ref().clone()).map_or_else(
            propagate!("Failed to parse path {}", u.as_ref()),
            |p| {
                for endpoint in endpoints.iter() {
                    if path::Path::overlap(&endpoint.path, &p) {
                        return Ok(endpoint.name.as_str());
                    }
                }

                return frierr!("Could not match any of the endpoints on the url");
            });
    }

}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn match_on_path_static() {
        let endpoints = vec![
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
        ];

        assert_eq!(Endpoint::match_on_path("/", &endpoints).unwrap(), "home");
        assert_eq!(Endpoint::match_on_path("/index.html", &endpoints).unwrap(), "index");
        assert_eq!(Endpoint::match_on_path("/static/", &endpoints).unwrap(), "static");
        assert_eq!(Endpoint::match_on_path("/static/home.js", &endpoints).unwrap(), "static");
        assert!(Endpoint::match_on_path("/woo/home.js", &endpoints).is_err());
    }

}
