fn main() {
   println!("cargo:rustc-link-lib=tensorflow");
   println!("cargo:rustc-link-lib=tensorflow_framework");
}
