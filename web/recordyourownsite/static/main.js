window.URL = window.URL || window.webkitURL;
window.AudioContext = window.AudioContext || window.webkitAudioContext;

navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia;

class AudioController {

    constructor() {
        this.context = null;
        this.recorder = null;
        this.playerSource = null;
        this.mediaStreamSource = null;
        this.audio_element = document.querySelector('audio');

        if (navigator.getUserMedia) {
            navigator.getUserMedia({audio: true},
                this.onSuccessfullyGettingMedia,
                this.onFailedGettingMedia);

        } else {
            console.log('navigator.getUserMedia not present');
            console.log('Recording will not work..');
        }

        this.clipCounter = 0;
    }

    onSuccessfullyGettingMedia = (s) => {
        this.context = new AudioContext();
        this.mediaStreamSource = this.context.createMediaStreamSource(s);
        this.recorder = new Recorder(this.mediaStreamSource);
    }

    onFailedGettingMedia = (e) => {
        console.log('Failed to get media!', e);
        console.log('This site wont work :(', e);
    }

    startRecording = () => {
        // Clear any previous sound
        this.recorder.clear();

        // Start recording new sound
        this.recorder.record();
        document.getElementById("record").classList.toggle("active-recording", true);
    }

    stopRecording = () => {
      document.getElementById("record").classList.toggle("active-recording", false);
      this.recorder.stop();
    }

    playRecording = (buffers) => {
      console.log("Buffers", buffers);
      var newSource = this.context.createBufferSource();
      var newBuffer = this.context.createBuffer( 2, buffers[0].length, this.context.sampleRate );
      newBuffer.getChannelData(0).set(buffers[0]);
      newBuffer.getChannelData(1).set(buffers[1]);
      newSource.buffer = newBuffer;

      newSource.connect( this.context.destination );
      newSource.start(0);
    }

    runRecording = () => {
        this.startRecording();
        setTimeout(() => {
          console.log("Gettin buffar!")
          console.log("Recordar!", this.recorder);
          this.recorder.getBuffers(this.playRecording);
          this.stopRecording()

          //console.log("Exporting!", this.recorder);
          //this.recorder.exportWAV(this.playRecording);

        }, 2000);
    }

    sendRecording = () => {
        var xhr = new XMLHttpRequest();

        this.recorder.exportWAV((s) => {
            var word = document.getElementById("keyword").textContent;

            var fd = new FormData();
            fd.append("keyword", word);
            fd.append("data", s);

            xhr.open("POST", "/recording");
            xhr.send(fd);

            document.getElementById("send").classList.toggle("active-send", true);
            document.getElementById("send").textContent = "Thank You";

            xhr.onreadystatechange = () => {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    this.clipCounter += 1;
                    console.log("Successfully sent file!")
                    getNextWord();

                    setTimeout(() => {
                        document.getElementById("send").textContent = "send";
                        document.getElementById("send").classList.toggle("active-send", false);
                    }, 500)

                }
            }
        });
    }
}


controller = new AudioController()

function getNextWord() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/next-word");
    xhr.send();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log("Successfully got next word!")
            document.getElementById("keyword").textContent = xhr.response;
            document.getElementById("clip-counter").textContent = "Sent: " + controller.clipCounter;
        }
    }
}


console.log("Hi");

document.getElementById("record").onclick = controller.runRecording;
document.getElementById("send").onclick = controller.sendRecording;
