use friday_error::FridayError;
use std::fmt;

pub enum Symbol {
    Own 
}

impl fmt::Display for Symbol {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Symbol::Own => f.write_str("**")
        }
    }
}

#[derive(Clone)]
pub struct Path {
    components: Vec<String>
}

impl Path {
    pub fn new<S: AsRef<str>>(path: S) -> Result<Path, FridayError> {
        // TODO: Maybe do some path validation?
        Ok(Path {
            components: path.as_ref()
                .split("/")
                .filter(|s| s.len() > 0)
                .map(|s| s.to_owned())
                .collect()
        })
    }

    pub fn safe_new<S: AsRef<str>>(path: S) -> Path {
        // Here we trust the input to be correct..
        // TODO: is there some better way to get compile-time guarantees
        // and retain nice UX for coding Web vendors?

        Path {
            components: path.as_ref()
                .split("/")
                .filter(|s| s.len() > 0)
                .map(|s| s.to_owned())
                .collect()
        }
    }

    fn is_own(s: Option<&String>) -> bool {
        if s.is_none() {
            return false;
        }

        return s.unwrap().eq(&Symbol::Own.to_string());
    }

    fn is_equal(a: Option<&String>, b: Option<&String>) -> bool {
        // Wish we could lift option values
        match a.map(|x| b.map(|y| x == y)) {
            None => false,
            Some(v) => match v {
                None => false,
                Some(v) => v
            }
        }
    }

    pub fn overlap(a: &Path, b: &Path) -> bool {
        // This functions check if two paths overlap
        // if paths use no special syntax this is the same as equivalence
        let mut a_it = a.components.iter();
        let mut b_it = b.components.iter();

        loop {
            let a_next = a_it.next();
            let b_next = b_it.next();

            // If both are None they match
            if a_next.is_none() && b_next.is_none() {
                return true;
            }

            // If one is own we have a match
            if Path::is_own(a_next) || Path::is_own(b_next) {
                return true;
            }

            // If they are not equal we don't have a match
            if !Path::is_equal(a_next, b_next) {
                return false;
            }
        }
    }
}

pub fn rel_from<S: AsRef<str>>(path: S, base: S) -> Option<String> {
    return Path::new(path).map_or_else(
        |_| None,
        |path| {
            let mut it = path.components.iter();
            loop {
                match it.next() {
                    None => return None,
                    Some(comp) => {
                        if comp == base.as_ref() {
                            return Some(it.fold(String::new(), |acc, v| acc + "/" + v))
                        }
                    }
                }
            }
        });
}

impl fmt::Debug for Path {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("\n").unwrap();
        for (i, entry) in self.components.iter().enumerate() {

            f.write_str(&i.to_string()).unwrap();
            f.write_str("   ").unwrap();
            f.write_str(&entry).unwrap();
            f.write_str("\n").unwrap();
        }

        f.write_str("\n").unwrap();
        return Ok(())
    }
}

impl fmt::Display for Path {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(
            self.components.iter()
                .fold(String::new(), |acc, v| acc + "/" + v)
                .as_str()
                ).unwrap();

        return Ok(())
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn make_path() {
        let mut path = Path::new("/hello/world").expect("Failed to make path");
        assert_eq!(path.components, vec!["hello", "world"]);

        path = Path::new("/").expect("Failed to make path");
        assert_eq!(path.components, Vec::<String>::new());

        path = Path::new("").expect("Failed to make path");
        assert_eq!(path.components, Vec::<String>::new());

        path = Path::new("/hello/world/").expect("Failed to make path");
        assert_eq!(path.components, vec!["hello", "world"]);
    }

    #[test]
    fn check_overlap() {
        let mut a = Path::new("/hello/world").expect("Failed to make path");
        let mut b = Path::new("/hello/world").expect("Failed to make path");

        assert!(Path::overlap(&a, &b));

        a = Path::new("/").expect("Failed to make path");
        b = Path::new("").expect("Failed to make path");

        assert!(Path::overlap(&a, &b));

        a = Path::new("/hello").expect("Failed to make path");
        b = Path::new("/hello/world").expect("Failed to make path");

        assert!(!Path::overlap(&a, &b));

        a = Path::new("hello").expect("Failed to make path");
        b = Path::new("/hello").expect("Failed to make path");

        // TODO: Is this a problem yay or nay?
        assert!(Path::overlap(&a, &b));

        a = Path::new(format!("/{}", Symbol::Own)).expect("");
        b = Path::new("/").expect("Failed to make path");

        assert!(Path::overlap(&a, &b));

        a = Path::new(format!("/static/{}", Symbol::Own)).expect("");
        b = Path::new("/static/hello.js").expect("Failed to make path");
        assert!(Path::overlap(&a, &b));

        a = Path::new(format!("/static/{}", Symbol::Own)).expect("");
        b = Path::new("/hue/").expect("");
        assert!(!Path::overlap(&a, &b));
    }
}
