use crate::core;
use std::time;
use friday_storage;
use std::sync::{RwLock, Arc};
use friday_error::{FridayError, propagate, frierr};
use ureq;
use pnet;

// Even if local IP has not changed we will ping remote with new
// ip once a day in-case that server forgets us or restarts.
static REFRESH_REMOTE: u64 = 3600 * 24;

// We will check for changes in local IP once an hour
static REFRESH_LOCAL: u64 = 3600;

use serde_derive::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
struct Config {
    local_ip: Option<String>,
    site_url: String,
}

pub struct KartaSite {
    config: Config,
    name: Arc<RwLock<String>>,
    port: u16,
    last_ip_update: time::Instant
}

#[derive(Serialize)]
struct Message {
    // The URL we had before sending this update
    old_url: Option<String>,
    // The URL we have now
    new_url: String,
    // Name of this friday (not necessarily unique)
    name: String
}

impl KartaSite {
    /// Creates a Karta that will ping a server with information about this Fridays
    /// IP on the local network. This lets a user go visit that site and be redirected to
    /// the friday without having to look-up the Fridays IP on the local network itself.
    pub fn new(name: Arc<RwLock<String>>, port: u16) -> Result<KartaSite, FridayError>  {
        return friday_storage::config::get_config("discovery_kartasite.json").map_or_else(
            propagate!("Failed to create KartaSite Karta"),
            |config| Ok(KartaSite {
                config,
                name,
                port,
                last_ip_update: time::Instant::now()
            }));
    }

    fn update_local_ip(&mut self, ip: String) {
        self.last_ip_update = time::Instant::now();
        self.config.local_ip = Some(ip);
    }

    /// Returns the first ipv4 address used in the network interface
    fn first_v4_ip(network: &pnet::datalink::NetworkInterface) -> Option<String> {
        network.ips
            .iter()
            .find(|n| n.is_ipv4())
            .map(|i| i.ip().to_string())
    }

    /// Returns the ip of the machine on the local network
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
            Some(interface) => match KartaSite::first_v4_ip(interface) {
                Some(network) => Ok(network),
                // TODO: Maybe ipv6 is ok too?
                None => frierr!("Found no valid ipv4 interface")
            },
            None => frierr!("Found no default interface on this machine")
        }
    }

    /// Returns the ip into a url that when used in a browser
    /// will redirect the user to the Friday web-interface of this machine.
    fn format_url(&self, ip: String) -> String {
        format!("http://{}:{}", ip, self.port)
    }

    /// Sends local IP to the remote server so that the server can redirect users to this local
    /// machine.
    fn send_ip(&mut self, old_ip: Option<String>, new_ip: String) -> Result<(), friday_error::FridayError> {
        match self.name.clone().read() {
            Err(err) => frierr!("Failed to aquire lock for name - Reason: {}", err),
            Ok(name) => match serde_json::to_value(Message{
                // Old URL - server can use it to remove if it wants
                old_url: old_ip.map(|u| self.format_url(u)),
                // URL that will redirect a user to this fridays local site
                new_url: self.format_url(new_ip.clone()),
                // Name of this Friday that the server can display if it wants
                // it is not guaranteed to be unique.
                name: name.clone()
            }) { 
                Err(err) => frierr!("Failed to serialize to serde::value - Reason: {}", err),
                Ok(value) => {
                    let response = ureq::put(self.config.site_url.as_str()).send_json(value);

                    if response.status() == 200 {
                        // If we managed to update our IP remotely we update our current local IP
                        self.update_local_ip(new_ip.clone());

                        // Little logging to show that we successfully sent discovery to site
                        println!(
                            "Discovery: {} status {}", 
                            self.config.site_url, 
                            response.status());

                        return Ok(());
                    } else {
                        return frierr!("Received status {} when seding IP using KartaSite", 
                            response.status());
                    }
                }
            }
        }
    }
}

impl core::Karta for KartaSite {
    fn name(&self) -> String { "KartaSite".to_owned() }

    // Check if local IP changes every X seconds
    fn time_to_clue(&self) -> time::Duration { time::Duration::from_secs(REFRESH_LOCAL) }

    fn clue(&mut self) -> Result<(), friday_error::FridayError> {
        // TODO: Might want to notify remote server if our local IP changes so that it can
        // remove that IP from itself? 
        match KartaSite::get_local_ip() {
            Err(err) => propagate!("Failed to get local IP")(err),
            Ok(new_local_ip) => match self.config.local_ip.clone() {
                // Tell server that this is our local ip! 
                None => self.send_ip(None, new_local_ip.clone()),
                Some(old_local_ip) => {

                    // If old local ip does not match current local ip - we must 
                    // server to remove of our old IP and add our new IP!
                    if old_local_ip != new_local_ip {
                        self.send_ip(Some(old_local_ip), new_local_ip.clone())
                    } 
                    // Update remote even if local has not changed
                    // In case remote has forgot us due to restart or something
                    else if time::Instant::now()
                        .duration_since(self.last_ip_update)
                            .as_secs() > REFRESH_REMOTE {
                        // We just None for old - so that the server
                        // won't try to remove it - if the server removes
                        // in wrong order it might add new ip and then remove it
                        // since they are the same. This guarantees that even if
                        // server is poorly coded it won't remove our ip :)
                        self.send_ip(None, new_local_ip.clone())
                    } 
                    // Do nothing - all is good! :)
                    else {
                        Ok(())
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
        KartaSite::new(name, 8000).expect("Failed to create KartaSite");
    }

    #[test]
    fn get_local_ip() {
        println!("{}", KartaSite::get_local_ip().expect("Failed to get local URL"));
    }
}
