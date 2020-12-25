mod core;
mod ping_site;
pub mod discovery;

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    #[test]
    fn create_discovery() {
        env::set_var("FRIDAY_CONFIG", "./test-resources");

        let discovery_handle = discovery::Discovery::new(8000)
            .expect("Failed to create discovery").make_discoverable();

        discovery_handle.wait();
    }

}
