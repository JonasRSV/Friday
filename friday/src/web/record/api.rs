use std::sync::{Arc, Mutex};
use friday_audio::recorder::Recorder;
use friday_error::{FridayError, propagate, frierr};
use friday_web;
use friday_storage;
use friday_logging;
use crate::web::record::core;

pub struct WebRecord {
    endpoints: Vec<friday_web::endpoint::Endpoint>,
    shared_istream: Arc<Mutex<dyn Recorder + Send>>,
    files: friday_storage::files::Files

}

impl WebRecord {
    pub fn new(shared_istream: Arc<Mutex<dyn Recorder + Send>>) -> Result<WebRecord, FridayError> {
        friday_storage::config::get_config_directory().map_or_else(
            propagate!("Failed to create 'WebRecord'"), 
            |mut config_dir| {
                // We store all recordings in 'CONFIG_ROOT/recordings'
                config_dir.push("recordings");
                friday_storage::files::Files::new(config_dir).map_or_else(
                    propagate!("Failed to create 'WebRecord'"), 
                    |files| 
                    Ok(WebRecord {
                        endpoints: vec![
                            // Record new clip and return clip ID
                            friday_web::endpoint::Endpoint{ 
                                name: "new".to_owned(),
                                methods: vec![
                                    friday_web::core::Method::Get
                                ],
                                path: friday_web::path::Path::safe_new(
                                    "/record/new")
                            },
                            // Return wav-file of clip given ID
                            friday_web::endpoint::Endpoint{ 
                                name: "listen".to_owned(),
                                methods: vec![
                                    friday_web::core::Method::Post
                                ],
                                path: friday_web::path::Path::safe_new(
                                    "/record/listen")
                            },              
                            // Update name of a recording
                            friday_web::endpoint::Endpoint{ 
                                name: "rename".to_owned(),
                                methods: vec![
                                    friday_web::core::Method::Put
                                ],
                                path: friday_web::path::Path::safe_new(
                                    "/record/rename")
                            },
                            // Remove a wav-file given ID
                            friday_web::endpoint::Endpoint{ 
                                name: "remove".to_owned(),
                                methods: vec![
                                    friday_web::core::Method::Put
                                ],
                                path: friday_web::path::Path::safe_new(
                                    "/record/remove")
                            },
                            // Returns IDs of all clips
                            friday_web::endpoint::Endpoint{ 
                                name: "clips".to_owned(),
                                methods: vec![
                                    friday_web::core::Method::Get
                                ],
                                path: friday_web::path::Path::safe_new(
                                    "/record/clips")
                            }
                        ],

                        shared_istream,
                        files
                    })
                )
            })
    }

    /// Record an audio clip, give it an ID and store it on disk
    fn record(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.shared_istream.lock() {
            Err(err) => frierr!("Failed to aquire lock for shared audio recording, Reason: {:?}",
                err),
            Ok(istream) => {
                friday_logging::info!("Recording...");
                // Sleep for 1.8 seconds to let the buffer fill
                std::thread::sleep(std::time::Duration::from_millis(2000));
                // Then we read the buffer store to file
                match istream.read() {
                    None => frierr!("Failed to read audio stream"),
                    Some(audio) => 
                        match self.files.store_audio(
                            core::random_file_id(), 
                            audio, 
                            istream.sample_rate()) {
                            Err(err) => propagate!("Failed to record audio file")(err), 
                            Ok(file_name) => friday_web::json!(
                                200,
                                &core::RecordResponse {
                                    id: file_name
                                })
                        }
                }
            }
        }
    }

    /// Return audio file corresponding to the ID
    fn listen(&self, req: core::ListenRequest) -> Result<friday_web::core::Response, FridayError> {
        match self.files.get_file(req.id) {
            Err(err) => propagate!("Failed to get file for listening")(err),
            Ok(file) => Ok( friday_web::core::Response::FILE 
                { 
                    status: 200, 
                    file,  
                    content_type: "audio/wav".to_owned()
                })
        }
    }

    /// Remove the audio file corresponding to the ID
    fn remove(&self, req: core::RemoveRequest) -> Result<friday_web::core::Response, FridayError> {
        friday_logging::info!("Removing {}", req.id);
        match self.files.remove_file(req.id) {
            Err(err) => propagate!("Failed to remove recording")(err),
            Ok(_) => friday_web::ok!("Successfully removed file")
        }
    }

    /// Rename the audio file corresponding to the ID
    fn rename(&self, req: core::RenameRequest) -> Result<friday_web::core::Response, FridayError> {
        match self.files.rename(req.old_id, req.new_id) {
            Err(err) => propagate!("Failed to rename recording")(err),
            Ok(_) => friday_web::ok!("Successfully renamed file")
        }        
    }

    /// Return IDs of all audio files
    fn clips(&self) -> Result<friday_web::core::Response, FridayError> {
        match self.files.list_files_under("") {
            Err(err) => propagate!("Failed to list clips")(err),
            Ok(ids) => friday_web::json!(
                200,
                &core::ClipsResponse {
                    ids
                }
            )
        }
    }
}

impl friday_web::vendor::Vendor for WebRecord {
    fn name(&self) -> String { return "record".to_owned() }
    fn endpoints(&self) -> Vec<friday_web::endpoint::Endpoint> { return self.endpoints.clone(); }

    fn handle(&mut self, r: &mut dyn friday_web::core::FridayRequest) -> 
        Result<friday_web::core::Response, FridayError> {
            match friday_web::get_name(r, &self.endpoints) {
                Err(err) => propagate!("Failed to get 'Record' endpoint for {}", r.url())(err),
                Ok(name) => match name.as_str() {
                    "new" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Get => self.record(),
                        m => friday_web::not_acceptable!("Only Get is accepted for 'WebRecord'\
                            'new' endpoint I received: {:?}", m)

                    },
                    "listen" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Post => friday_web::request_json(r, &|d| self.listen(d)),
                        m => friday_web::not_acceptable!("Only Post is accepted for 'WebRecord'\
                            'listen' endpoint I received: {:?}", m)

                    },
                    "remove" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Put => friday_web::request_json(r, &|d| self.remove(d)),
                        m => friday_web::not_acceptable!("Only Put is accepted for 'WebRecord'\
                            'remove' endpoint I received: {:?}", m)

                    },
                    "rename" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Put => friday_web::request_json(r, &|d| self.rename(d)),
                        m => friday_web::not_acceptable!("Only Put is accepted for 'WebRecord'\
                            'rename' endpoint I received: {:?}", m)

                    }
                    "clips" => match r.method() { 
                        // This gets all lights
                        friday_web::core::Method::Get => self.clips(),
                        m => friday_web::not_acceptable!("Only Get is accepted for 'WebRecord'\
                            'clips' endpoint I received: {:?}", m)

                    },
                    _ => frierr!("Unknown endpoint name {}", name)
                }
            }

    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;  
    use friday_audio;
    use std::env;
    use ureq;

    #[test]
    fn record_new_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let r = friday_audio::RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = 
            friday_audio::friday_cpal::CPALIStream::record(&r)
            .expect("Failed to start audio recording");

        let web_record_vendor = Arc::new(Mutex::new(WebRecord::new(istream).expect("Failed to create 'WebRecord'")));


        let mut server = friday_web::server::Server::new().expect("Failed to create friday web server");
        server.register(vec![
            web_record_vendor.clone()
        ]).expect("Failed to register web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/record/new").call();

        assert!(resp.status() == 200);

        let response_data : core::RecordResponse = 
            resp.into_json_deserialize::<core::RecordResponse>()
            .expect("Failed to parse json response");

        println!("{:?}", response_data);

        web_record_vendor.lock().unwrap().files.remove_file(response_data.id).expect("Failed to remove file");

        handle.stop();
    }

    #[test]
    fn record_remove_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let r = friday_audio::RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = 
            friday_audio::friday_cpal::CPALIStream::record(&r)
            .expect("Failed to start audio recording");

        let web_record_vendor = Arc::new(
            Mutex::new(
                WebRecord::new(istream).expect("Failed to create 'WebRecord'")
                )
            );

        let mut server = friday_web::server::Server::new().expect("Failed to create friday web server");
        server.register(vec![
            web_record_vendor.clone()
        ]).expect("Failed to register web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        File::create("./test-resources/recordings/tmp_file").expect("Failed to create file");
        assert!(web_record_vendor.lock().unwrap().files.exists("tmp_file"));

        let resp = ureq::put("http://0.0.0.0:8000/record/remove")
            .send_json(serde_json::to_value(core::RemoveRequest {
                id: "tmp_file".to_owned()
            }).expect("Failed to serialize state"));

        assert!(resp.status() == 200);

        handle.stop();
    }

    #[test]
    fn record_rename_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let r = friday_audio::RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = 
            friday_audio::friday_cpal::CPALIStream::record(&r)
            .expect("Failed to start audio recording");

        let web_record_vendor = Arc::new(
            Mutex::new(
                WebRecord::new(istream).expect("Failed to create 'WebRecord'")
                )
            );

        let mut server = friday_web::server::Server::new().expect("Failed to create friday web server");
        server.register(vec![
            web_record_vendor.clone()
        ]).expect("Failed to register web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        File::create("./test-resources/recordings/tmp_file").expect("Failed to create file");
        assert!(web_record_vendor.lock().unwrap().files.exists("tmp_file"));

        let resp = ureq::put("http://0.0.0.0:8000/record/rename")
            .send_json(serde_json::to_value(core::RenameRequest {
                old_id: "tmp_file".to_owned(),
                new_id: "new_tmp_file".to_owned()
            }).expect("Failed to serialize state"));

        assert!(resp.status() == 200);

        assert!(web_record_vendor.lock().unwrap().files.exists("new_tmp_file"));
        assert!(!web_record_vendor.lock().unwrap().files.exists("tmp_file"));

        let resp = ureq::put("http://0.0.0.0:8000/record/remove")
            .send_json(serde_json::to_value(core::RemoveRequest {
                id: "new_tmp_file".to_owned()
            }).expect("failed to serialize state"));

        assert!(resp.status() == 200);

        handle.stop();
    }

    #[test]
    fn record_clips_via_web() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        env::set_var("FRIDAY_GUI", ".");

        let r = friday_audio::RecordingConfig {
            sample_rate: 8000,
            model_frame_size: 16000
        };


        let istream = 
            friday_audio::friday_cpal::CPALIStream::record(&r)
            .expect("Failed to start audio recording");

        let web_record_vendor = Arc::new(
            Mutex::new(
                WebRecord::new(istream).expect("Failed to create 'WebRecord'")
                )
            );


        let mut server = friday_web::server::Server::new().expect("Failed to create friday web server");
        server.register(vec![
            web_record_vendor.clone()
        ]).expect("Failed to register web vendor");

        let handle = server.listen("0.0.0.0:8000").expect("Failed to start server");

        std::thread::sleep(std::time::Duration::from_millis(1000));

        let resp = ureq::get("http://0.0.0.0:8000/record/clips").call();

        assert!(resp.status() == 200);

        let response_data : core::ClipsResponse = 
            resp.into_json_deserialize::<core::ClipsResponse>()
            .expect("Failed to parse json response");

        println!("{:?}", response_data);

        assert_eq!(response_data.ids, vec!["test.wav", "test_2.wav"]);

        handle.stop();
    }
}
