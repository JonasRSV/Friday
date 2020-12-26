use friday_error::FridayError;
use std::time::Duration;

#[derive(Eq, PartialEq, PartialOrd, Ord)]
pub enum Status<A> {
    Continue(A),
    Retry(A, Duration),
    Exit
}

// Karta is the swedish word for map
// Each Karta will guide a user towards Friday.
pub trait Karta {
    // Used for error logging etc
    fn name(&self) -> String;

    // This is an approximate time since if other Kartas
    // takes up much time this cannot be guaranteed.
    fn time_to_clue(&self) -> Duration;

    // The clue can be anything - e.g say we ping a site
    // or try to receive access to wifi via bluetooth or whatever
    fn clue(&mut self) -> Result<(), FridayError>;
}
