use lazy_static::lazy_static;
use std::time;
use humantime;
use ansi_term::Color;
use std::env;

// TODO: Maybe we want to have some global static singleton that does
// different things for these depending on some settings?
//





lazy_static! {
    pub static ref LEVEL: u32 = match env::var("FRIDAY_LOG_LEVEL") {
        Err(_) => 5,
        Ok(s) => match s.as_str() {
            "DEBUG" => 5,
            "INFO" => 4,
            "WARNING" => 3,
            "ERROR" => 2,
            "FATAL" => 1,
            _ => 5
        }
    };
}
    



pub fn get_timestamp() -> String {
    return humantime::format_rfc3339_seconds(time::SystemTime::now()).to_string();
}

pub fn extract_filename(file_path: &str) -> String {
    match file_path.split("/").last() {
        Some(f) => f.to_owned(),
        None => "unknown".to_owned()
    }
}

pub fn red<S: AsRef<str>>(s: S) -> String {
    Color::Red.paint(s.as_ref()).to_string()
}

pub fn green<S: AsRef<str>>(s: S) -> String {
    Color::Green.paint(s.as_ref()).to_string()
}

pub fn yellow<S: AsRef<str>>(s: S) -> String {
    Color::Yellow.paint(s.as_ref()).to_string()
}

pub fn cyan<S: AsRef<str>>(s: S) -> String {
    Color::Cyan.paint(s.as_ref()).to_string()
}

pub fn purple<S: AsRef<str>>(s: S) -> String {
    Color::Purple.paint(s.as_ref()).to_string()
}

pub fn blue<S: AsRef<str>>(s: S) -> String {
    Color::Blue.paint(s.as_ref()).to_string()
}

pub fn white<S: AsRef<str>>(s: S) -> String {
    Color::Blue.paint(s.as_ref()).to_string()
}


#[macro_export]
macro_rules! debug {
    ($str:expr $(,$arg: expr)*) => {
        if *$crate::LEVEL > 4 {
            println!("{}", 
                $crate::yellow(
                    format!(
                        "{} {}:{} - {}", 
                        $crate::get_timestamp(), 
                        $crate::extract_filename(std::file!()), 
                        std::line!(), 
                        format!($str $(,$arg)*)
                    )
                )
            );
        }
    }
}

#[macro_export]
macro_rules! info {
    ($str:expr $(,$arg: expr)*) => {
        if *$crate::LEVEL > 3 {
            println!("{}", 
                $crate::blue(
                    format!(
                        "{} {}:{} - {}", 
                        $crate::get_timestamp(), 
                        $crate::extract_filename(std::file!()), 
                        std::line!(), 
                        format!($str $(,$arg)*)
                    )
                )
            );
        }
    }
}

#[macro_export]
macro_rules! warning {
    ($str:expr $(,$arg: expr)*) => {
        if *$crate::LEVEL > 2 {
            println!("{}", 
                $crate::purple(
                    format!(
                        "{} {}:{} - {}", 
                        $crate::get_timestamp(), 
                        $crate::extract_filename(std::file!()), 
                        std::line!(), 
                        format!($str $(,$arg)*)
                    )
                )
            );
        }
    }
}

#[macro_export]
macro_rules! error {
    ($str:expr $(,$arg: expr)*) => {
        if *$crate::LEVEL > 1 {
            println!("{}", 
                $crate::red(
                    format!(
                        "{} {}:{} - {}", 
                        $crate::get_timestamp(), 
                        $crate::extract_filename(std::file!()), 
                        std::line!(), 
                        format!($str $(,$arg)*)
                    )
                )
            );
        }
    }
}

#[macro_export]
macro_rules! fatal {
    ($str:expr $(,$arg: expr)*) => {
        if *$crate::LEVEL > 0 {
            println!("{}", 
                $crate::red(
                    format!(
                        "{} {}:{} - {}", 
                        $crate::get_timestamp(), 
                        $crate::extract_filename(std::file!()), 
                        std::line!(), 
                        format!($str $(,$arg)*)
                    )
                )
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn log_debug() {
        debug!("Hello {}", "debug")
    }

    #[test]
    fn log_info() {
        info!("Hello {}", "info")
    }

    #[test]
    fn log_warning() {
        warning!("Hello {}", "warning")
    }

    #[test]
    fn log_error() {
        error!("Hello {}", "error")
    }

    #[test]
    fn log_fatal() {
        fatal!("Hello {}", "fatal")
    }
}
