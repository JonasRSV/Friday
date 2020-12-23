use huelib;
use serde_derive::{Deserialize, Serialize};
use crate::core::State;



/// This module exists because huelib does not 
/// derive Serialize on its Lights struct
/// So I am using this to be able to serialize and de-serialize
/// lights to send them over the web
#[derive(Deserialize, Serialize, Clone)]
pub struct Light {
    id: String,
    name: String,
    kind: String,
    state: State,
    model_id: String,
    unique_id: String,
    product_id: Option<String>,
    product_name: Option<String>,
    manufacturer_name: Option<String>,
    software_version: String,

}

// Here we implement conversion traits to make it easy to convert between the two representations
// Just by implementing these two - rust can make use of them to convert
// Collections of Lights between each-other etc - very cool! :p

impl From<huelib::resource::Light> for Light {
    fn from(light: huelib::resource::Light) -> Self {
        Light {
            id: light.id,
            name: light.name,
            kind: light.kind,
            state: State {
                on: light.state.on,
                brightness: light.state.brightness,
                saturation: light.state.saturation,
                hue: light.state.hue
            },
            model_id: light.model_id,
            unique_id: light.unique_id,
            product_id: light.product_id,
            product_name: light.product_name,
            manufacturer_name: light.manufacturer_name,
            software_version: light.software_version
        }
    }
}

impl From<Light> for huelib::resource::Light {
    fn from(light: Light) -> huelib::resource::Light {
        huelib::resource::Light {
            id: light.id,
            name: light.name,
            kind: light.kind,
            state: huelib::resource::light::State {
                on: light.state.on,
                brightness: light.state.brightness,
                saturation: light.state.saturation,
                hue: light.state.hue,
                color_space_coordinates: None,
                color_temperature: None,
                alert: None,
                effect: None,
                color_mode: None,
                reachable: true,
            },
            model_id: light.model_id,
            unique_id: light.unique_id,
            product_id: light.product_id,
            product_name: light.product_name,
            manufacturer_name: light.manufacturer_name,
            software_version: light.software_version,
            software_update: huelib::resource::light::SoftwareUpdate {
                state:  huelib::resource::light::SoftwareUpdateState::NoUpdates,
                last_install: None
            },
            config: huelib::resource::light::Config {
                arche_type: "".to_owned(),
                function: "".to_owned(),
                direction: "".to_owned(),
                startup: None,

            },
            capabilities: huelib::resource::light::Capabilities {
                certified: true,
                control: huelib::resource::light::ControlCapabilities {
                    min_dimlevel: None,
                    max_lumen: None,
                    color_gamut: None,
                    color_gamut_type: None,
                    color_temperature: None,

                },
                streaming: huelib::resource::light::StreamingCapabilities {
                    renderer: false,
                    proxy: false,

                },

            },
        }

    }
}

