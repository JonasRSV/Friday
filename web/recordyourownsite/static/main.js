document.getElementById("info-tile").textContent = "Loaded Website.. if you see this something went terribly wrong!";
window.URL = window.URL || window.webkitURL;
window.AudioContext = window.AudioContext || window.webkitAudioContext;


var isRecording = false;
var isSending = false;

class AudioController {

    constructor() {
        this.current_audio_blob = null;

        this.context = null;
        this.recorder = null;
        this.playerSource = null;
        this.mediaStreamSource = null;
        this.analyser = null;

        document.getElementById("info-tile").textContent = "Trying to get media!";

        this.context = new(window.AudioContext || window.webkitAudioContext)();
        if (this.context.createJavaScriptNode) {
            this.audioNode = this.context.createJavaScriptNode(1024, 2, 2);
        } else if (this.context.createScriptProcessor) {
            this.audioNode = this.context.createScriptProcessor(1024, 2, 2);
        } else {
            document.getElementById("info-tile").textContent = "Webaudio is not supported";
            throw 'WebAudio not supported!';
        }

        this.audioNode.connect(this.context.destination);

        window.navigator.mediaDevices.getUserMedia({
                audio: true,
                video: false
            })
            .then(this.onSuccessfullyGettingMedia)
            .catch(this.onFailedGettingMedia);

        this.clipCounter = 0;

        this.audioBuffer = new Uint8Array();
    }

    paintAudioWave = () => {
      var canvas = document.getElementById("audio-canvas");
      var canvasCtx = canvas.getContext("2d");
      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

      var bufferLength = this.analyser.frequencyBinCount;
      var dataArray = new Uint8Array(bufferLength);
      this.analyser.getByteTimeDomainData(dataArray);

      var newAudioBuffer = new Uint8Array(dataArray.length + this.audioBuffer.length);
      newAudioBuffer.set(this.audioBuffer);
      newAudioBuffer.set(dataArray, this.audioBuffer.length);

      this.audioBuffer = newAudioBuffer;

      console.log("height", canvas.height)

      var height = canvas.height;
      var x = 0;
      var sliceWidth = canvas.width / 20000 ;
      canvasCtx.beginPath();
      canvasCtx.moveTo(0, height / 2);
      for (var i = 0; i < this.audioBuffer.length; i++) {
        var v = this.audioBuffer[i] / 128.0;
        var y = v * height / 2;


        canvasCtx.lineTo(x, y);
        x += sliceWidth;

        //console.log("x", x, "y", y);

      }
      //canvasCtx.lineTo(canvas.width, canvas.height/2);
      canvasCtx.strokeStyle = '#008000'; 
      canvasCtx.lineWidth = 0.5;
      canvasCtx.stroke();
    }

    onSuccessfullyGettingMedia = (s) => {
        document.getElementById("info-tile").textContent = "Got UserMedia!";
        document.getElementById("info-tile").classList.toggle("green-text", true);
        this.mediaStreamSource = this.context.createMediaStreamSource(s);
        this.mediaStreamSource.connect(this.audioNode)

        this.analyser = this.context.createAnalyser();
        this.analyser.fftSize = 2048;
        this.mediaStreamSource.connect(this.analyser);

        this.recorder = new Recorder(this.mediaStreamSource, this.audioNode);
    }

    onFailedGettingMedia = (e) => {
        document.getElementById("info-tile").textContent = "Failed to get media";
        console.log('Failed to get media!', e);
        console.log('This site wont work :(', e);
    }

    startRecording = () => {
        this.context.resume();


        document.getElementById("info-tile").textContent = "Clearing Previous";
        // Clear any previous sound
        this.recorder.clear();
        // Start recording new sound
        document.getElementById("info-tile").textContent = "Recording";
        this.recorder.record();
    }

    stopRecording = () => {
        document.getElementById("info-tile").textContent = "Stopping Recording";
        this.recorder.stop();
        document.getElementById("info-tile").textContent = "Stopped Recording";
    }

    playRecording = (blob) => {
        this.current_audio_blob = blob;
        const url = URL.createObjectURL(blob)
        var audio = new Audio(url);
        audio.play();
        document.getElementById("info-tile").textContent = "Played audio of size " + blob.size + " If you're on IPhone you have to click the title to get playback";
    }

    runRecording = () => {
        isRecording = true;

        var btn = document.getElementById("record");
        btn.disabled = true;
        btn.innerHTML = "<span class='spinner-grow spinner-grow-sm' role='status' aria-hidden='true'></span>"

        this.startRecording();
        
        var animation = setInterval(this.paintAudioWave, 100);


        setTimeout(() => {
            this.stopRecording()
            isRecording = false;
            this.recorder.exportWAV(this.playRecording);

            btn.disabled = false;
            btn.innerHTML = "Spela in";

            clearTimeout(animation);
            this.audioBuffer = new Uint8Array();

        }, 2000);

    }

    sendRecording = () => {
        isSending = true;
        var btn = document.getElementById("send");
        btn.disabled = true;
        btn.innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>"

        var xhr = new XMLHttpRequest();

        this.recorder.exportWAV((s) => {
            var word = document.getElementById("keyword").textContent;

            var fd = new FormData();
            fd.append("keyword", word);
            fd.append("data", s);

            console.log("Sending", s);

            xhr.open("POST", "/recording");
            xhr.send(fd);

            xhr.onreadystatechange = () => {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    this.clipCounter += 1;
                    console.log("Successfully sent file!")
                    getNextWord();


                    isSending = false;
                    btn.disabled = false;
                    btn.innerHTML = "Skicka"
                }
            }
        });
    }
}



document.getElementById("info-tile").textContent = "Made controller!";
controller = new AudioController()


function getNextWord() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/next-word");
    xhr.send();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log("Successfully got next word!")
            document.getElementById("keyword").textContent = xhr.response;
            document.getElementById("info-tile").textContent = "Sent: " + controller.clipCounter;
        }
    }
}



document.getElementById("record").onclick = () => {
    controller.runRecording();
    document.getElementById("info-tile").textContent = "Managed to start recording";
}

document.getElementById("send").onclick = controller.sendRecording;

document.getElementById("keyword").onclick = () => {
    const url = URL.createObjectURL(controller.current_audio_blob)
    var audio = new Audio(url);
    audio.play();
    document.getElementById("info-tile").textContent = "Played audio of size " + controller.current_audio_blob.size;
}

document.onkeydown = (ev) => {
    if (!isRecording && !isSending) {
        if (ev.keyCode == 32) {
            controller.runRecording();
        }
        if (ev.keyCode == 13) {
            controller.sendRecording();
        }
    }
}


