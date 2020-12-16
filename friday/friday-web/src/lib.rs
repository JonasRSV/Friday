use url;
use tiny_http;
use friday_error::FridayError;
use friday_error::frierr;
use std::sync::Arc;
use std::sync::Mutex;
use std::thread;


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
    methods: Vec<Method>,
    path: String
}

pub enum Data {
    Empty,
    Bytes {d: Vec<u8>}
}

pub enum ContentType {
    JSON,
    TEXT,
    Unknown
}

pub trait FridayRequest {
    fn method(&self) -> Method;
    fn content_type(&self) -> ContentType;
    fn data(&mut self) -> Data;
    fn url(&self) -> String;
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

    fn content_type(&self) -> ContentType {
        return match self.headers().iter().position(
            |header| header.field.to_string() == "Content-Type") {
            Some(index) => {
                let content_type = self.headers()[index].value.to_string();
                match content_type.as_str() {
                    "application/json" => ContentType::JSON,
                    "text/plain" => ContentType::TEXT,
                    _ => ContentType::Unknown
                }
            }
            None => ContentType::Unknown
        }
    }

    fn data(&mut self) -> Data {
        let mut content = Vec::new();
        return self.as_reader().read_to_end(&mut content).map_or_else(
            |_| Data::Empty,
            |_| {
                if content.len() > 0 {
                    return Data::Bytes {d: content};
                }
                return Data::Empty;
            });
    }

    fn url(&self) -> String {
        return String::from(format!("http://{}{}", self.remote_addr(), self.url()));
    }
}

pub enum Response {
    Empty{status: i32},
    JSON {status: i32, content: String},
    TEXT {status: i32, content: String}
}


pub trait Vendor {
    fn name(&self) -> String;
    fn endpoints(&self) -> Vec<EndPoint>;
    fn handle(&mut self, r: &dyn FridayRequest) -> Result<Response, FridayError>;
}


#[derive(Clone)]
pub struct Server {
    vendors: Vec<Arc<Mutex<dyn Vendor + Send>>>,
}

pub enum ServerResponseStatus {
    Responded,
    AttemptedResponse {err: String},
    FailedToRespond {err: String}
}


impl Server {
    pub fn new() -> Server {
        return Server{
            vendors: Vec::new(),
        };
    }

    fn status_500(r: tiny_http::Request) {
        match r.respond(
            tiny_http::Response::from_string("Something went wrong..")
            .with_status_code(500)) {
            Ok(()) => (),
            Err(err) => println!("Failed to send 500 response to client - Reason: {}", err)
        }
    }

    fn status_400(r: tiny_http::Request) {
        match r.respond(
            tiny_http::Response::from_string("Did not find that endpoint..")
            .with_status_code(400)) {
            Ok(()) => (),
            Err(err) => println!("Failed to send 400 response to client - Reason: {}", err)
        }
    }

    pub fn register(&mut self, vedors: Vec<Arc<Mutex<dyn Vendor + Send>>>) -> Result<(), FridayError> { 
        // TODO do checks that we dont have conflicting endpoints

        // Naive Validation of endpoints
        // Will probably never have more than 10 so this is should not be a problem
        for (i, vi) in vedors.iter().enumerate() {
            for (j, vj) in vedors.iter().enumerate() {
                if i != j {
                    // TODO deal with lock failures
                    let vi_endpoints = vi.lock().expect("Failed to aquire lock").endpoints();
                    let vj_endpoints = vj.lock().expect("Failed to aquire lock").endpoints();

                    for i_endpoint in vi_endpoints.iter() {
                        for j_endpoint in vj_endpoints.iter() {
                            if i_endpoint.path == j_endpoint.path {
                                return frierr!("{} and {} shares the path {}",
                                    vi.lock().expect("Failed to aquire lock").name(), 
                                    vj.lock().expect("Failed to aquire lock").name(), i_endpoint.path);
                            }
                        }
                    }
                }
            }
        }

        self.vendors = vedors.clone();

        return Ok(());
    }

    pub fn listen<S>(&mut self, connection: S) -> Result<(), FridayError>
        where S: AsRef<str> {
            eprintln!("Starting Server on {}", connection.as_ref());

            return tiny_http::Server::http(connection.as_ref()).map_or_else(
                |err| frierr!("Failed to start Server {} - Reason: {}", connection.as_ref(), err),
                |server| {
                    let server = Arc::new(server);
                    // Start two threads
                    let mut server_handles = Vec::new();
                    for _ in 0..2 { 
                        let server = server.clone();
                        // Needed because we do not want to move self into the new thread.
                        let self_reference = Box::new(self.clone());

                        server_handles.push(
                            thread::spawn(
                                move || {
                                    let server_ref = self_reference;
                                    for r in server.incoming_requests() {
                                        Server::handle_request(r, &server_ref)
                                    }
                                }
                            )
                        );
                    }

                    for handle in server_handles {
                        handle.join().expect("Failed to join thread"); 
                    }

                    return Ok(());

                });
    }

    fn handle_request(r: tiny_http::Request, self_reference: &Box<Server>) {
        match self_reference.lookup(&r) {
            Ok(locked_vendor) => 
                match locked_vendor.lock() {
                    Ok(mut vendor) => self_reference.dispatch_vendor(&mut (*vendor), r),
                    Err(err) => {
                        println!("Failed to aquire mutex lock - Reason: {}", err);
                        Server::status_500(r);
                    }
                },
            Err(err) => {
                println!("Failed to find vendor for this request - Reason: {:?}", err);
                Server::status_400(r);
            }
        };

    }


    fn dispatch_vendor(&self, v: &mut dyn Vendor, r: tiny_http::Request) {
        match v.handle(&r) {
            Ok(response) => 
                match response {
                    Response::Empty{status: _} => todo!(),
                    Response::JSON{status: _, content: _} => todo!(),
                    Response::TEXT{status: s, content: text} => {
                        let success_string = format!("Success! {} {} {}", r.method(), r.remote_addr(), r.url());
                        match r.respond(tiny_http::Response::from_string(text)
                            .with_status_code(s)) {
                            Ok(_) => println!("{}", success_string),
                            Err(err) => println!("Failed to send text response - Reason: {}", err)
                        }
                    }
                },
            Err(err) => {
                println!("Vendor failed - Reason: {:?}", err);
                Server::status_500(r);
            }
        }
    }

    fn lookup(&self, r: &dyn FridayRequest) -> Result<Arc<Mutex<dyn Vendor + Send>>, FridayError> {
        // TODO
        // If this is slow build a trie in the register and use that instead

        let request_method = r.method();
        return url::Url::parse(&r.url()).map_or_else(
            |err| frierr!("Failed to parse http URL {} - Reason: {}", r.url(), err),
            |url| {
                // TODO add logic for handling url args here at some point if needed.
                let path = url.path();

                for vedors in self.vendors.iter() {

                    // TODO deal with lock failures
                    let endpoints = vedors.lock().expect("Failed to aquire lock in lookup").endpoints();
                    for endpoint in endpoints.iter() {
                        for method in endpoint.methods.clone() {
                            if request_method == method && path == endpoint.path {
                                return Ok(vedors.clone());
                            }
                        }
                    }
                }
                todo!()
            })
    }
}




#[cfg(test)]
mod tests {
    use super::*;

    struct MockVendor {}
    impl Vendor for MockVendor {
        fn name(&self) -> String { return String::from("MockVendor"); }
        fn endpoints(&self) -> Vec<EndPoint> {
            return vec![
                EndPoint{
                    methods: vec![Method::Get, Method::Post],
                    path: String::from("/")
                },
                EndPoint{
                    methods: vec![Method::Get],
                    path: String::from("/home")
                }
            ]
        }
        fn handle(&mut self, _: &dyn FridayRequest) -> Result<Response, FridayError> {
            todo!()
        }
    }

    struct CollidingVendor {}
    impl Vendor for CollidingVendor {
        fn name(&self) -> String { return String::from("CollidingVendor"); }
        fn endpoints(&self) -> Vec<EndPoint> {
            return vec![
                EndPoint{
                    methods: vec![Method::Get, Method::Post],
                    path: String::from("/home")
                },
            ]
        }

        fn handle(&mut self, _: &dyn FridayRequest) -> Result<Response, FridayError> {
            todo!()
        }
    }

    struct MockRequest {
        url: String,
        method: Method
    }

    impl FridayRequest for MockRequest {
        fn method(&self) -> Method { return self.method.clone(); }
        fn content_type(&self) -> ContentType { todo!() }
        fn data(&mut self) -> Data { return Data::Empty; }
        fn url(&self) -> String { return self.url.clone(); }

    }

    #[test]
    fn try_lookup() {
        let mut server = Server::new();

        let failed_register = server.register(
            vec![Arc::new(Mutex::new(MockVendor{})),
            Arc::new(Mutex::new(CollidingVendor{}))]

        );

        assert!(failed_register.is_err());

        server.register(
            vec![Arc::new(Mutex::new(MockVendor{}))]
        ).expect("Failed to register vedors");




        let r = MockRequest {
            url: String::from("http://recordyourownsites.se/home"),
            method: Method::Get
        };

        let vedors = server.lookup(&r).expect("No vedors found");

        assert_eq!(vedors.lock().expect("Failed to aquire lock").name(), String::from("MockVendor"));
    }

    struct IncrementNumberVendor { number: i32 }
    impl Vendor for IncrementNumberVendor {
        fn name(&self) -> String { return String::from("IncrementNumberVendor"); }
        fn endpoints(&self) -> Vec<EndPoint> {
            return vec![
                EndPoint{
                    methods: vec![Method::Get, Method::Post],
                    path: String::from("/")
                },
            ]
        }
        fn handle(&mut self, r: &dyn FridayRequest) -> Result<Response, FridayError> {
            let url = url::Url::parse(&r.url()).expect("Failed to parse url");
            return match url.path() {
                "/" => {
                    self.number += 1;
                    return Ok(
                        Response::TEXT{
                            content: self.number.to_string(),
                            status: 200
                        });
                }
                _ => frierr!("{} does not support path {}", self.name(), url.path())
            }
        }
    }

    #[test]
    fn simple_increment_number_mock_server() {
        let mut server = Server::new();
        server.register(
            vec![Arc::new(Mutex::new(IncrementNumberVendor{number: 0}))]
        ).expect("Failed to register vedors");


        let r = MockRequest {
            url: String::from("http://recordyourownsites.se/"),
            method: Method::Get
        };

        let vedors = server.lookup(&r).expect("No vedors found");
        assert_eq!(vedors.lock().expect("Unable to aquire mutex").name(), String::from("IncrementNumberVendor"));

        server.listen("0.0.0.0:8000").expect("Failed to launch server");
    }
}
