use std::collections::HashMap;
use serde_derive::{Deserialize, Serialize};

pub static HUE_LOGIN_TIMEOUT: u64 = 30;
pub static HUE_CREDENTIAL_FILE: &str = "philips_hue_credentials.json";
pub static HUE_CONFIG_FILE: &str = "philips_hue.json";
pub static HUE_USER : &str = "friday-voice-assistant";


#[derive(Deserialize, Serialize)]
pub struct HueLogin {
    pub ip: String,
    pub user: String
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct State {
    pub on: Option<bool>,
    pub brightness: Option<u8>,
    pub hue: Option<u16>,
    pub saturation: Option<u8>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct LightUpdate {
    pub id: String,
    pub state: State
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct HueCommandConfig {
    pub lights: HashMap<String, Vec<LightUpdate>>
}

impl From<huelib::resource::Light> for LightUpdate {
    fn from(light: huelib::resource::Light) -> Self {
        LightUpdate {
            id: light.id,
            state: State {
                on: light.state.on,
                brightness: light.state.brightness,
                saturation: light.state.saturation,
                hue: light.state.hue
            },
        }
    }
}
