var onFail = function(e) {
  console.log('Rejected!', e);
};

window.AudioContext = window.AudioContext || window.webkitAudioContext;

var onSuccess = function(s) {
  var context = new AudioContext();
  var mediaStreamSource = context.createMediaStreamSource(s);
  recorder = new Recorder(mediaStreamSource);
  recorder.record();
}

window.URL = window.URL || window.webkitURL;
navigator.getUserMedia  = navigator.getUserMedia 
  || navigator.webkitGetUserMedia 
  || navigator.mozGetUserMedia 
  || navigator.msGetUserMedia;

var recorder;
var audio = document.querySelector('audio');
var clipCounter = 0;

function runRecording() {
  startRecording();
  setTimeout(stopRecording, 2000);
}


function startRecording() {
  if (navigator.getUserMedia) {
    navigator.getUserMedia({audio: true}, onSuccess, onFail);
    document.getElementById("record").classList.toggle("active-recording", true);
  } else {
    console.log('navigator.getUserMedia not present');
  }
}

function stopRecording() {
  document.getElementById("record").classList.toggle("active-recording", false);
  recorder.stop();
  recorder.exportWAV(function(s) {
    audio.src = window.URL.createObjectURL(s);
  });
}

function getNextWord() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET","/next-word");    
    xhr.send();

    xhr.onreadystatechange = function() {
      if(xhr.readyState == 4 && xhr.status == 200) {
        console.log("Successfully got next word!")
        document.getElementById("keyword").textContent = xhr.response;
        document.getElementById("clip-counter").textContent = "Sent: " + clipCounter;
      }
    }
}

function sendRecording() {
  var xhr = new XMLHttpRequest();

  recorder.exportWAV(function(s) {
    word = document.getElementById("keyword").textContent;

    var fd = new FormData();
    fd.append("keyword", word);
    fd.append("data", s);

    xhr.open("POST","/recording");    
    xhr.send(fd);

    document.getElementById("send").classList.toggle("active-send", true);
    document.getElementById("send").textContent = "Thank You";

    xhr.onreadystatechange = function() {
      if(xhr.readyState == 4 && xhr.status == 200) {
        clipCounter += 1;
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
