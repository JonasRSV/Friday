document.getElementById("info-tile").textContent = "Loaded Website.. if you see this something went terribly wrong!";
window.URL = window.URL || window.webkitURL;
window.AudioContext = window.AudioContext || window.webkitAudioContext;


class AudioController {

    constructor() {
	this.current_audio_blob = null;

        this.context = null;
        this.recorder = null;
        this.playerSource = null;
        this.mediaStreamSource = null;

        document.getElementById("info-tile").textContent = "Trying to get media!";

        this.context = new (window.AudioContext || window.webkitAudioContext)();
        if (this.context.createJavaScriptNode) {
            	this.audioNode = this.context.createJavaScriptNode(1024, 1, 1);
        } else if (this.context.createScriptProcessor) {
            	this.audioNode = this.context.createScriptProcessor(1024, 1, 1);
        } else {
		document.getElementById("info-tile").textContent = "Webaudio is not supported";
            	throw 'WebAudio not supported!';
        }

        this.audioNode.connect(this.context.destination);

        window.navigator.mediaDevices.getUserMedia({audio: true, video: false})
	  .then(this.onSuccessfullyGettingMedia)
	  .catch(this.onFailedGettingMedia);

        this.clipCounter = 0;
    }

    onSuccessfullyGettingMedia = (s) => {
        document.getElementById("info-tile").textContent = "Got UserMedia!";
        this.mediaStreamSource = this.context.createMediaStreamSource(s);
	this.mediaStreamSource.connect(this.audioNode)
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
        this.recorder.record();
        document.getElementById("record").classList.toggle("active-recording", true);
    }

    stopRecording = () => {
      document.getElementById("record").classList.toggle("active-recording", false);
      document.getElementById("info-tile").textContent = "Stopping Recording";
      this.recorder.stop();
      document.getElementById("info-tile").textContent = "Stopped Recording";
    }

    playRecording = (blob) => {
      this.current_audio_blob = blob;
      const url = URL.createObjectURL(blob)
      var audio = new Audio(url);
      audio.play();
      document.getElementById("info-tile").textContent = "Played audio of size " + blob.size + " If you're on phone you might have to click the title to get playback";
    }

    runRecording = () => {
        this.startRecording();
        setTimeout(() => {
          this.stopRecording()
          this.recorder.exportMonoWAV(this.playRecording);

        }, 2000);

    }

    sendRecording = () => {
        var xhr = new XMLHttpRequest();

        this.recorder.exportMonoWAV((s) => {
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

