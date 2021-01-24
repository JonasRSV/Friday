use serde_derive::{Deserialize, Serialize};
use rand::Rng;

#[derive(Serialize, Debug, Deserialize)]
pub struct RecordResponse {
    pub id: String
}

#[derive(Deserialize, Debug)]
pub struct ListenRequest {
    pub id: String
}

#[derive(Deserialize, Debug)]
pub struct RemoveRequest {
    pub id: String
}

#[derive(Deserialize, Debug)]
pub struct RenameRequest {
    pub old_id: String, 
    pub new_id: String
}

#[derive(Serialize, Debug, Deserialize)]
pub struct ClipsResponse {
    pub ids: Vec<String>
}

pub fn random_file_id() -> String {
    let mut rng = rand::thread_rng();

    format!("{}-{}-{}-{}", 
        rng.gen_range(0, 999),
        rng.gen_range(0, 999),
        rng.gen_range(0, 999),
        rng.gen_range(0, 999))
}
