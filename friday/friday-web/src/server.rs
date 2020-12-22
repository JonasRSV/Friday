use url;
use tiny_http;
use std::str::FromStr;
use friday_error::FridayError;
use friday_error::frierr;
use friday_error::propagate;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use crate::webgui::WebGui;

use crate::core::{FridayRequest, Vendor,  Response};



#[derive(Clone)]
pub struct Server {
    vendors: Vec<Arc<Mutex<dyn Vendor + Send>>>,
    webgui: Arc<Mutex<WebGui>>,

    pub running: Arc<AtomicBool>
}


impl Server {
    pub fn new() -> Result<Server, FridayError> {
        return WebGui::new().map_or_else(
            propagate!("Unable to get 'WebGui' vendor"),
            |s| Ok( Server {
                vendors: Vec::new(),
                webgui: Arc::new(Mutex::new(s)),
                running: Arc::new(AtomicBool::new(true))

            }));
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

    pub fn register(&mut self, vendors: Vec<Arc<Mutex<dyn Vendor + Send>>>) -> Result<(), FridayError> { 
        // TODO do checks that we dont have conflicting endpoints

        // Naive Validation of endpoints
        // Will probably never have more than 10 so this is should not be a problem
        for (i, vi) in vendors.iter().enumerate() {
            for (j, vj) in vendors.iter().enumerate() {
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

        self.vendors = vendors.clone();

        return Ok(());
    }

    pub fn listen<S>(&mut self, connection: S) -> Result<Vec<thread::JoinHandle<()>>, FridayError>
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
                                    loop {
                                        match server.recv_timeout(std::time::Duration::from_secs(5)) {
                                            Ok(maybe_request) => match maybe_request {
                                                Some(request) => Server::handle_request(
                                                    request, 
                                                    &server_ref),
                                                None => ()
                                            },
                                            Err(err) => println!("Error while receiving request - Reason: {}", 
                                                err)
                                        }

                                        // If we received a signal to quit we break out of the loop
                                        if !server_ref.running.load(Ordering::Relaxed) { break; }
                                    }
                                }
                            )
                            );
                    }

                    return Ok(server_handles);
                });
        }

    fn handle_request(r: tiny_http::Request, self_reference: &Box<Server>) {
        let method = r.method().clone();
        let address = r.remote_addr().clone();
        let url = String::from(r.url());

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
                println!("400 {} {} {} - Reason: {:?}", method, address, url, err);
                Server::status_400(r);
            }
        };

    }


    fn dispatch_vendor(&self, v: &mut dyn Vendor, mut r: tiny_http::Request) {
        let method = r.method().clone();
        let address = r.remote_addr().clone();
        let url = String::from(r.url());

        match v.handle(&mut r) {
            Ok(response) =>  {
                match response {
                    Response::Empty{status: _} => todo!(),
                    Response::JSON{status:_, content:_} => todo!(),
                    Response::TEXT{status, content} => 
                        match r.respond(tiny_http::Response::from_string(content)
                            .with_status_code(status)) {
                            Ok(_) => println!("{} {} {} {}", status, method, address, url),
                            Err(err) => println!("Failed to send text response - Reason: {}", err)
                        },
                        Response::FILE{status, file, content_type} => 
                            tiny_http::Header::from_str(format!("Content-Type: {}", content_type).as_str()
                                ).map_or_else(
                                |_| println!("Failed to send file response because header construction failed"),
                                |header| 
                                match r.respond(tiny_http::Response::from_file(file)
                                    .with_status_code(status)
                                    .with_header(header)) {
                                    Ok(_) => println!("{} {} {} {}", status, method, address, url),
                                    Err(err) => println!("Failed to send file response - Reason: {}", err)
                                }

                            )
                }
            }, 
            Err(err) => {
                println!("Web Vendor failed - Reason: {:?}", err);
                Server::status_500(r);
            }
        }
    }

    pub fn lookup(&self, r: &dyn FridayRequest) -> Result<Arc<Mutex<dyn Vendor + Send>>, FridayError> {
        // TODO
        // If this is slow build a trie in the register and use that instead
        let request_method = r.method();
        return url::Url::parse(&r.url()).map_or_else(
            |err| frierr!("Failed to parse http URL {} - Reason: {}", r.url(), err),
            |url| {
                // TODO add logic for handling url args here at some point if needed.
                let path = url.path();

                for vendor in self.vendors.iter() {

                    // TODO deal with lock failures
                    let endpoints = vendor.lock().expect("Failed to aquire lock in lookup").endpoints();
                    for endpoint in endpoints.iter() {
                        for method in endpoint.methods.clone() {
                            if request_method == method && path == endpoint.path {
                                return Ok(vendor.clone());
                            }
                        }
                    }
                }


                // If we do not find a vendor for it - it must be a special vendor.. or bad url

                // Here we do some simple URL parsing..
                let mut path_it = path.split("/");

                // Drop empty before root.. so splitting "/static/.." gives ["", "static",..]
                path_it.next();

                match path_it.next() {
                        None => Ok(self.webgui.clone()), // Return homepage for ''
                        Some(sub_path) => match sub_path {
                            "static" => Ok(self.webgui.clone()),
                            "" => Ok(self.webgui.clone()), // Return homepage for '/'
                            _ => frierr!("Found no matching handler for {} - {}", sub_path, path)
                    }
                }

                });
    }
}
