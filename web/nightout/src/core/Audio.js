
export function playAudio(stream) {
  console.log("stream", stream)
  stream.body.getReader().read().then(audio => {
    console.log("audio", audio)
    let blob = new Blob([audio.value], { type: 'audio/wav' });
    let url = window.URL.createObjectURL(blob)
    window.audio = new Audio();
    window.audio.src = url;
    window.audio.play();
  })
}
