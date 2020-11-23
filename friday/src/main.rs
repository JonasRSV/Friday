use audio_io;

fn main() {
    println!("Hello, world!");

    let config = audio_io::RecordingConfig {
        sample_rate: 8000,
        buffer_size: 2000,
        model_frame_size: 16000
    };

    let istream = audio_io::record(&config);

    std::thread::sleep(std::time::Duration::from_secs(1));
    match istream.read() {
        Some(v) => println!("{:?}", v[0..1000].iter()),
        _ => println!("Failed to read")
    }

    std::thread::sleep(std::time::Duration::from_secs(2));
    println!();

    match istream.read() {
        Some(v) => println!("{:?}", v[0..1000].iter()),
        _ => println!("Failed to read")
    }


    drop(istream);
}
