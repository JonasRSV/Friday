use crate::core;
use std::time;
use friday_storage;
use std::sync::{RwLock, Arc};
use friday_error::{FridayError, propagate, frierr};
use ureq;
use pnet;

use serde_derive::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
struct PingConfig {
    local_ip: Option<String>,
    site_url: String,
}

pub struct PingSite {
    config: PingConfig,
    name: Arc<RwLock<String>>,
    port: u16

}

#[derive(Serialize)]
struct PingMessage {
    url: String,
    name: String
}

impl PingSite {
    pub fn new(name: Arc<RwLock<String>>, port: u16) -> Result<PingSite, FridayError>  {
        return friday_storage::config::get_config("discovery_ping_site.json").map_or_else(
            propagate!("Failed to create PingSite Lighthouse"),
            |config| Ok(PingSite {
                config,
                name,
                port
            }));
    }

    fn first_v4_ip(network: &pnet::datalink::NetworkInterface) -> Option<String> {
        network.ips
            .iter()
            .find(|n| n.is_ipv4())
            .map(|i| i.ip().to_string())
    }

    pub fn get_local_ip() -> Result<String, FridayError> {
        // Apparently the default interface for the machine is the one that is
        // 1. Up
        // Is not a loopback
        // and has an IP
        // So we will use this as the local URL
        let interfaces = pnet::datalink::interfaces();
        //
        let default_interface = interfaces
            .iter()
            .find(|e| e.is_up() && !e.is_loopback() && !e.ips.is_empty());


        match default_interface {
            Some(interface) => match PingSite::first_v4_ip(interface) {
                Some(network) => Ok(network),
                // TODO: Maybe ipv6 is ok too?
                None => frierr!("Found no valid ipv4 interface")
            },
            None => frierr!("Found no default interface on this machine")
        }
    }

    fn format_url(&self, ip: String) -> String {
        format!("http://{}:{}", ip, self.port)
    }

    fn send_site_ping(&mut self, ip: String) -> Result<core::Blip, friday_error::FridayError> {
        match self.name.read() {
            Err(err) => frierr!("Failed to aquire lock for name - Reason: {}", err),
            Ok(name) => match serde_json::to_value(PingMessage{
                url: self.format_url(ip.clone()),
                name: name.clone()
            }) { 
                Err(err) => frierr!("Failed to serialize to serde::value - Reason: {}", err),
                Ok(value) => {
                    let response = ureq::put(self.config.site_url.as_str()).send_json(value);

                    if response.status() == 200 {
                        self.config.local_ip = Some(ip.clone());
                        println!("Discovery: {} status {}", 
                            self.config.site_url, 
                            response.status());
                        return Ok(core::Blip::Ok);
                    } else {
                        return frierr!("Received status {} from pinging discovery site", 
                            response.status());
                    }
                }
            }
        }
    }
}

impl core::LightHouse for PingSite {
    fn name(&self) -> String { "PingSite".to_owned() }

    // Check if local IP changes every 10 minutes
    fn time_between_blip(&self) -> time::Duration { time::Duration::from_secs(600) }

    fn blip(&mut self) -> Result<core::Blip, friday_error::FridayError> {
        // TODO: Even if the remote site responds with 200
        // We might want to still re-send at some point in the future
        // since the server might be restarted or forget us
        match PingSite::get_local_ip() {
            Err(err) => propagate!("Failed to get local URL")(err),
            Ok(new_local_ip) => match self.config.local_ip.clone() {
                None => self.send_site_ping(new_local_ip.clone()),
                Some(old_local_ip) => {
                    // So here we maybe want to check if enough time has passed
                    // we do site ping anyway
                    if old_local_ip != new_local_ip {
                        self.send_site_ping(new_local_ip.clone())
                    } else {
                        Ok(core::Blip::Ok)
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    #[test]
    fn create_ping_site() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");
        let name = Arc::new(RwLock::new("hi".to_owned()));
        PingSite::new(name, 8000).expect("Failed to create PingSite");
    }

    #[test]
    fn get_local_ip() {
        println!("{}", PingSite::get_local_ip().expect("Failed to get local URL"));
    }
}
