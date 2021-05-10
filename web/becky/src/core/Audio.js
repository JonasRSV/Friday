export let audioCache = {};

export function loadAudioBlob(id, stream) {
  return extractAudioBlob(stream).then(url => {
    audioCache[id] = url;

    return "ok";
  });
}

function extractAudioBlob(stream) {

  let reader = stream.body.getReader();


  var audio = new Uint8Array();
  let processAudio = ({done, value}) => {
    // value is undefined if done is true
    if (done) {
      let blob = new Blob([audio], { type: 'audio/wav' });
      let url = window.URL.createObjectURL(blob)
      return url;
    }


    let concat_audio = new Uint8Array(audio.length + value.length);
    concat_audio.set(audio);
    concat_audio.set(value, audio.length);

    audio = concat_audio;

    return reader.read().then(processAudio);
  }

  return reader.read().then(processAudio);
}

export function playAudio(id) {
    let url = audioCache[id];


    window.audio = new Audio();
    window.audio.src = url;
    window.audio.play();
}
