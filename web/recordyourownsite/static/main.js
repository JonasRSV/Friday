document.getElementById("clip-counter").textContent = "Loaded Website and ran JS!";
window.URL = window.URL || window.webkitURL;
window.AudioContext = window.AudioContext || window.webkitAudioContext;


class AudioController {

    constructor() {
        this.context = null;
        this.recorder = null;
        this.playerSource = null;
        this.mediaStreamSource = null;

        document.getElementById("clip-counter").textContent = "Trying to get media!";

        this.context = new (window.AudioContext || window.webkitAudioContext)();
        if (this.context.createJavaScriptNode) {
            	this.audioNode = this.context.createJavaScriptNode(4096, 1, 1);
        } else if (this.context.createScriptProcessor) {
            	this.audioNode = this.context.createScriptProcessor(4096, 1, 1);
        } else {
		document.getElementById("clip-counter").textContent = "Webaudio is not supported";
            	throw 'WebAudio not supported!';
        }

        this.audioNode.connect(this.context.destination);

        window.navigator.mediaDevices.getUserMedia({audio: true, video: false})
	  .then(this.onSuccessfullyGettingMedia)
	  .catch(this.onFailedGettingMedia);

        this.clipCounter = 0;
    }

    onSuccessfullyGettingMedia = (s) => {
        document.getElementById("clip-counter").textContent = "Got UserMedia!";
        this.mediaStreamSource = this.context.createMediaStreamSource(s);
	this.mediaStreamSource.connect(this.audioNode)
        this.recorder = new Recorder(this.mediaStreamSource);
    }

    onFailedGettingMedia = (e) => {
	document.getElementById("clip-counter").textContent = "Failed to get media";
        console.log('Failed to get media!', e);
        console.log('This site wont work :(', e);
    }

    startRecording = () => {


	document.getElementById("clip-counter").textContent = "Clearing Previous";
        // Clear any previous sound
        this.recorder.clear();
        // Start recording new sound
        this.recorder.record();
        document.getElementById("record").classList.toggle("active-recording", true);
    }

    stopRecording = () => {
      document.getElementById("record").classList.toggle("active-recording", false);
      document.getElementById("clip-counter").textContent = "Stopping Recording";
      this.recorder.stop();
      document.getElementById("clip-counter").textContent = "Stopped Recording";
    }

    playRecording = (buffers) => {
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
          this.stopRecording()
          document.getElementById("clip-counter").textContent = "Getting buffers to playback";
          this.recorder.getBuffers(this.playRecording);

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

            console.log("Sending", s);

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



document.getElementById("clip-counter").textContent = "Made controller!";
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



document.getElementById("record").onclick = () => {
	controller.runRecording();
	document.getElementById("clip-counter").textContent = "Managed to run recording";
}

document.getElementById("send").onclick = controller.sendRecording;

