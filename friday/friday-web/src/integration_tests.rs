
#[cfg(test)]
mod tests {
    use crate::server::*;
    use crate::core::*;
    use friday_error::FridayError;
    use friday_error::frierr;
    use std::sync::Arc;
    use std::sync::Mutex;

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
        fn handle(&mut self, _: &mut dyn FridayRequest) -> Result<Response, FridayError> {
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

        fn handle(&mut self, _: &mut dyn FridayRequest) -> Result<Response, FridayError> {
            todo!()
        }
    }

    struct MockRequest {
        url: String,
        method: Method
    }

    impl FridayRequest for MockRequest {
        fn method(&self) -> Method { return self.method.clone(); }
        fn data(&mut self) -> Result<Data, FridayError> { return Ok(Data::Empty); }
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
        fn handle(&mut self, r: &mut dyn FridayRequest) -> Result<Response, FridayError> {
            let url = url::Url::parse(&r.url()).expect("Failed to parse url");

            let request_data_message = r.data().map_or_else(
                |err| format!("Failed to fetch data - Reason: {:?}", err),
                |data| {
                    match data {
                        Data::Empty => String::from("Data is empty"),
                        Data::TEXT {text} => text,
                        Data::JSON {json} => json
                    }

                });

            println!("Request data is: {}", request_data_message);

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

        let handles = server.listen("0.0.0.0:8000").expect("Failed to launch server");

        for handle in handles {
            handle.join().expect("Failed to join thread");
        }
    }
}
