/// This module houses the webserver that drives the web vendors of Friday
/// Today it is implemented using tiny_http - TODO: Move to tokio in future to improve
/// performance.

use url;
use tiny_http;
use std::str::FromStr;
use friday_error::{FridayError, frierr, propagate};
use friday_logging;
use std::sync::Arc;
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;

use crate::webgui::WebGui;
use crate::path;

use crate::core::{FridayRequest, Response};
use crate::vendor::Vendor;


pub struct ServerHandle {
    handles: Vec<thread::JoinHandle<()>>,
    running: Arc<AtomicBool>
}

impl ServerHandle {
    pub fn stop(self) {
        self.running.swap(false, Ordering::Relaxed);
        for handle in self.handles {
            handle.join().expect("Failed to join WebServer thread");
        }
    }

    pub fn wait(self) {
        for handle in self.handles {
            handle.join().expect("Failed to join WebServer thread");
        }
    }
}

#[derive(Clone)]
pub struct Server {
    vendors: Vec<Arc<Mutex<dyn Vendor + Send>>>,
    pub running: Arc<AtomicBool>
}


impl Server {
    pub fn new() -> Result<Server, FridayError> {
        return WebGui::new().map_or_else(
            propagate!("Unable to get 'WebGui' vendor"),
            |s| Ok( Server {
                vendors: vec![Arc::new(Mutex::new(s))],
                running: Arc::new(AtomicBool::new(true))

            }));
    }

    fn status_500(r: tiny_http::Request) {
        match r.respond(
            tiny_http::Response::from_string("Something went wrong..")
            .with_status_code(500)) {
            Ok(()) => (),
            Err(err) => friday_logging::warning!("Failed to send 500 response to client - Reason: {}", err)
        }
    }

    fn status_400(r: tiny_http::Request) {
        match r.respond(
            tiny_http::Response::from_string("Did not find that endpoint..")
            .with_status_code(400)) {
            Ok(()) => (),
            Err(err) => friday_logging::warning!("Failed to send 400 response to client - Reason: {}", err)
        }
    }

    pub fn register(&mut self, mut vendors: Vec<Arc<Mutex<dyn Vendor + Send>>>) -> Result<(), FridayError> { 
        // Add self to make sure we're not colliding to anything already there
        vendors.extend(self.vendors.clone());

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
                            if path::Path::overlap(&i_endpoint.path, &j_endpoint.path) {
                                return frierr!("{} and {} overlaps on - {} and {} -",
                                    vi.lock().expect("Failed to aquire lock").name(), 
                                    vj.lock().expect("Failed to aquire lock").name(), 
                                    i_endpoint.path,
                                    j_endpoint.path);
                            }
                        }
                    }
                }
            }
        }

        self.vendors = vendors.clone();

        return Ok(());
    }

    pub fn listen<S>(&mut self, connection: S) -> Result<ServerHandle, FridayError>
        where S: AsRef<str> {
            friday_logging::info!("Starting Server on {}", connection.as_ref());

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
                                            Err(err) => friday_logging::warning!(
                                                "Error while receiving request - Reason: {}", 
                                                err)
                                        }

                                        // If we received a signal to quit we break out of the loop
                                        if !server_ref.running.load(Ordering::Relaxed) { break; }
                                    }
                                }
                            )
                            );
                    }

                    return Ok(ServerHandle {
                        handles: server_handles,
                        running: self.running.clone()
                    });
                });
        }

    fn handle_request(r: tiny_http::Request, self_reference: &Box<Server>) {
        let method = r.method().clone();
        let address = r.remote_addr().clone();
        let url = String::from(r.url());

        match self_reference.lookup(&r) {
            Ok(locked_vendor) => 
                // This can be a bottleneck if a client is only talking to one
                // vendor - since here we're synchronizing all threads so that only
                // on thread is run per vendor. This synchronization makes writing vendors
                // much less painful - but perhaps at a too great cost?
                //
                // It is probably not a problem but worth investigating if performance becomes
                // an issue
                match locked_vendor.lock() {
                    Ok(mut vendor) => self_reference.dispatch_vendor(&mut (*vendor), r),
                    Err(err) => {
                        friday_logging::fatal!("Failed to aquire mutex lock - Reason: {}", err);

                        // To avoid any spamming - We do not deal well with mutex poisoning
                        // and it should never happend
                        thread::sleep(std::time::Duration::from_millis(500));

                        Server::status_500(r);
                    }
                },
            Err(err) => {
                friday_logging::warning!("400 {} {} {} - Reason: {:?}", method, address, url, err);
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
                    Response::Empty{status} => 
                        match r.respond(tiny_http::Response::from_string("")
                                        .with_status_code(status)) {
                            Ok(_) => friday_logging::info!("{} {} {} {}", status, method, address, url),
                            Err(err) => friday_logging::warning!("Failed to send empty response - Reason: {}", err)
                    },
                    Response::JSON{status, content} => 
                             tiny_http::Header::from_str("Content-Type:  application/json").map_or_else(
                                |_| friday_logging::warning!(
                                    "Failed to send json response because header construction failed"),
                                |header| 
                        match r.respond(tiny_http::Response::from_string(content)
                            .with_status_code(status)
                            .with_header(header)) {
                                Ok(_) => friday_logging::info!("{} {} {} {}", status, method, address, url),
                                Err(err) => friday_logging::warning!(
                                    "Failed to send json response - Reason: {}", err)
                    }),
                    Response::TEXT{status, content} => 
                        match r.respond(tiny_http::Response::from_string(content)
                            .with_status_code(status)) {
                            Ok(_) => friday_logging::info!("{} {} {} {}", status, method, address, url),
                            Err(err) => friday_logging::warning!(
                                "Failed to send text response - Reason: {}", err)
                    },
                    Response::FILE{status, file, content_type} => 
                            tiny_http::Header::from_str(format!("Content-Type: {}", content_type).as_str()
                                ).map_or_else(
                                |_| friday_logging::warning!(
                                    "Failed to send file response because header construction failed"),
                                |header| 
                                match r.respond(tiny_http::Response::from_file(file)
                                    .with_status_code(status)
                                    .with_header(header)) {
                                    Ok(_) => friday_logging::info!("{} {} {} {}", status, method, address, url),
                                    Err(err) => friday_logging::warning!(
                                        "Failed to send file response - Reason: {}", err)
                                }

                    )
                }
            }, 
            Err(err) => {
                friday_logging::warning!("Web Vendor failed - Reason: {:?}", err);
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
            |url| path::Path::new(url.path()).map_or_else(
                    propagate!("Failed to create path from a valid path"),
                    |path| {
                        for vendor in self.vendors.iter() {

                            // TODO deal with lock failures
                            let endpoints = vendor.lock().expect("Failed to aquire lock in lookup").endpoints();
                            for endpoint in endpoints.iter() {
                                for method in endpoint.methods.clone() {
                                    if request_method == method && path::Path::overlap(&path, &endpoint.path) {
                                        return Ok(vendor.clone());
                                    }
                                }
                            }
                        }
                        frierr!("Found no matching handler for {} ", path)

                    }));


    }
}

