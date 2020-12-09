(function(window) {

    var WORKER_PATH = 'static/recordWorker.js';
    var Recorder = function(source, node, cfg) {
        var config = cfg || {};
        var bufferLen = config.bufferLen || 4096;
        this.context = source.context;
        this.node = node;
        var worker = new Worker(config.workerPath || WORKER_PATH);
        worker.postMessage({
            command: 'init',
            config: {
                sampleRate: this.context.sampleRate
            }
        });
        var recording = false,
            currCallback;

        this.node.onaudioprocess = function(e) {
            if (!recording) return;
            worker.postMessage({
                command: 'record',
                buffer: [
                    e.inputBuffer.getChannelData(0),
                ]
            });
        }

        this.configure = function(cfg) {
            for (var prop in cfg) {
                if (cfg.hasOwnProperty(prop)) {
                    config[prop] = cfg[prop];
                }
            }
        }

        this.record = function() {

            recording = true;
        }

        this.stop = function() {

            recording = false;
        }

        this.clear = function() {
            worker.postMessage({
                command: 'clear'
            });
        }

        this.getBuffers = function(cb) {
          console.log("Getting em buffars!");
            currCallback = cb || config.callback;
          console.log("callback ", currCallback);
            worker.postMessage({
                command: 'getBuffers'
            })
        }

        this.exportMonoWAV = function(cb, type) {
            currCallback = cb || config.callback;
            type = type || config.type || 'audio/wav';
            if (!currCallback) throw new Error('Callback not set');
            worker.postMessage({
                command: 'exportMonoWAV',
                type: type
            });
        }

        worker.onmessage = function(e) {
          console.log("master got message", e);
            var blob = e.data;
            currCallback(blob);
        }
    };

    Recorder.forceDownload = function(blob, filename) {
        var url = (window.URL || window.webkitURL).createObjectURL(blob);
        var link = window.document.createElement('a');
        link.href = url;
        link.download = filename || 'output.wav';
        var click = document.createEvent("Event");
        click.initEvent("click", true, true);
        link.dispatchEvent(click);
    }

    window.Recorder = Recorder;

})(window);

