<script>
import { onMount } from "svelte";
import { FridayAPI } from "../../../FridayAPI.js";

export let onSync;
export let onSuccess;
export let onFailure;

let gotSync = false;
let gotSuccess = false;

let failed = true;


onMount (async () => { 
  let recordingPromise = FridayAPI.recordingNew();

  recordingPromise.then(recording => {
    failed = false;
    gotSync = true;

    onSync(recording.id).then(res => {
      console.log("got sync", res)

      gotSuccess = true;
      setTimeout(() => onSuccess(recording.id), 1000);
    })
  });

  setTimeout(() => {
    if (failed) {
      console.log("Probably Failed recording..");
      onFailure();
    }
  }, 8000);
});



</script>

<style>

.middle-screen {
  position: fixed;
  margin: 0 auto;
  top: 50%;
  left: 50%;

  /*To truly get it into the center*/
  transform: translate(-50%, -50%);
}

.loader,
.loader:before,
.loader:after {
  border-radius: 50%;
  width: 2.5em;
  height: 2.5em;
  -webkit-animation-fill-mode: both;
  animation-fill-mode: both;
  -webkit-animation: load7 1.8s infinite ease-in-out;
  animation: load7 1.2s infinite ease-in-out;
}
.loader {
  color: #ff6f00;
  font-size: 10px;
  margin: 80px auto;
  position: relative;
  text-indent: -9999em;
  -webkit-transform: translateZ(0);
  -ms-transform: translateZ(0);
  transform: translateZ(0);
  -webkit-animation-delay: -0.16s;
  animation-delay: -0.16s;
}
.loader:before,
.loader:after {
  content: '';
  position: absolute;
  top: 0;
}
.loader:before {
  left: -3.5em;
  -webkit-animation-delay: -0.32s;
  animation-delay: -0.32s;
}
.loader:after {
  left: 3.5em;
}
@-webkit-keyframes load7 {
  0%,
  80%,
  100% {
    box-shadow: 0 2.5em 0 -1.3em;
  }
  40% {
    box-shadow: 0 2.5em 0 0;
  }
}
@keyframes load7 {
  0%,
  80%,
  100% {
    box-shadow: 0 2.5em 0 -1.3em;
  }
  40% {
    box-shadow: 0 2.5em 0 0;
  }
}


.loader-container {
height: 40px;
width: 160px;
/*margin: 200px auto 0;*/
}

.loader-container > div {
  position: relative;
  display: inline-block;
  background: #03A9F4;
  height: 100%;
  width: 10px;
  margin: 0;
  -webkit-animation: load 2.0s ease-in-out infinite;
  animation: load 2.0s ease-in-out infinite;
}

.loader-container .rectangle-2 {
  -webkit-animation-delay: 0.1s;
  animation-delay: 0.1s;
}

.loader-container .rectangle-3 {
  -webkit-animation-delay: 0.2s;
  animation-delay: 0.2s;
}

.loader-container .rectangle-4 {
  -webkit-animation-delay: 0.3s;
  animation-delay: 0.3s;
}

.loader-container .rectangle-5 {
  -webkit-animation-delay: 0.4s;
  animation-delay: 0.4s;
}

.loader-container .rectangle-6 {
  -webkit-animation-delay: 0.5s;
  animation-delay: 0.5s;
}

@-moz-keyframes load {
  0%,
  100% {
    -moz-transform: scaleY(1);
    background: #03A9F4;
  }
  16.67% {
    -moz-transform: scaleY(3);
    background: #FF5722;
  }
  33.33% {
    -moz-transform: scaleY(1);
    background: #FF5252;
  }
  50% {
    -moz-transform: scaleY(3);
    background: #E91E63;
  }
  66.67% {
    -moz-transform: scaleY(1);
    background: #9C27B0;
  }
  83.34% {
    -moz-transform: scaleY(3);
    background: #673AB7;
  }
} 

@-webkit-keyframes load {
  0%,
  100% {
    -webkit-transform: scaleY(1);
    background: #03A9F4;
  }
  16.67% {
    -webkit-transform: scaleY(3);
    background: #FF5722;
  }
  33.33% {
    -webkit-transform: scaleY(1);
    background: #FF5252;
  }
  50% {
    -webkit-transform: scaleY(3);
    background: #E91E63;
  }
  66.67% {
    -webkit-transform: scaleY(1);
    background: #9C27B0;
  }
  83.34% {
    -webkit-transform: scaleY(3);
    background: #673AB7;
  }
} 

@keyframes load {
  0%,
  100% {
    transform: scaleY(1);
    background: #03A9F4;
  }
  16.67% {
    transform: scaleY(3);
    background: #FF5722;
  }
  33.33% {
    transform: scaleY(1);
    background: #FF5252;
  }
  50% {
    transform: scaleY(3);
    background: #E91E63;
  }
  66.67% {
    transform: scaleY(1);
    background: #9C27B0;
  }
  83.34% {
    transform: scaleY(3);
    background: #673AB7;
  }
}

/**
 * Extracted from: SweetAlert
 * Modified by: Istiak Tridip
 */

.check-icon {
  width: 80px;
  height: 80px;
  position: relative;
  border-radius: 50%;
  box-sizing: content-box;
  border: 4px solid #ff6f00;
}

.check-icon::before {
    top: 3px;
    left: -2px;
    width: 30px;
    transform-origin: 100% 50%;
    border-radius: 100px 0 0 100px;
}

.check-icon::after {
    top: 0;
    left: 30px;
    width: 60px;
    transform-origin: 0 50%;
    border-radius: 0 100px 100px 0;
    animation: rotate-circle 4.25s ease-in;
}

.check-icon:before, .check-icon::after {
    content: '';
    height: 100px;
    position: absolute;
    background: #303841;
    transform: rotate(-45deg);
}

.icon-line {
    height: 5px;
    background-color: #ff6f00;
    display: block;
    border-radius: 2px;
    position: absolute;
    z-index: 10;
}

.line-tip {
  top: 46px;
  left: 14px;
  width: 25px;
  transform: rotate(45deg);
  animation: icon-line-tip 0.75s;
}

.line-long {
  top: 38px;
  right: 8px;
  width: 47px;
  transform: rotate(-45deg);
  animation: icon-line-long 0.75s;
}


.icon-circle {
    top: -4px;
    left: -4px;
    z-index: 10;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    position: absolute;
    box-sizing: content-box;
    border: 4px solid rgba(255, 111, 0, .5);
}

.icon-fix {
    top: 8px;
    width: 5px;
    left: 26px;
    z-index: 1;
    height: 85px;
    position: absolute;
    transform: rotate(-45deg);
    background-color: #303841;
}
.success-checkmark {
    width: 80px;
    height: 115px;
    margin: 0 auto;
}

@keyframes rotate-circle {
    0% {
        transform: rotate(-45deg);
    }
    5% {
        transform: rotate(-45deg);
    }
    12% {
        transform: rotate(-405deg);
    }
    100% {
        transform: rotate(-405deg);
    }
}

@keyframes icon-line-tip {
    0% {
        width: 0;
        left: 1px;
        top: 19px;
    }
    54% {
        width: 0;
        left: 1px;
        top: 19px;
    }
    70% {
        width: 50px;
        left: -8px;
        top: 37px;
    }
    84% {
        width: 17px;
        left: 21px;
        top: 48px;
    }
    100% {
        width: 25px;
        left: 14px;
        top: 45px;
    }
}

@keyframes icon-line-long {
    0% {
        width: 0;
        right: 46px;
        top: 54px;
    }
    65% {
        width: 0;
        right: 46px;
        top: 54px;
    }
    84% {
        width: 55px;
        right: 0px;
        top: 35px;
    }
    100% {
        width: 47px;
        right: 8px;
        top: 38px;
    }
}

</style>

{#if gotSuccess}
<div class="middle-screen">
  <div class="success-checkmark">
    <div class="check-icon">
      <span class="icon-line line-tip"></span>
      <span class="icon-line line-long"></span>
      <div class="icon-circle"></div>
      <div class="icon-fix"></div>
    </div>
  </div>
</div>
{:else if gotSync}
<div class="middle-screen">
  <h6>Synchronizing Assistant</h6>
<div class="loader"></div>
</div>
{:else}
<div class="loader-container middle-screen">
    <div class="rectangle-1"></div>
    <div class="rectangle-2"></div>
    <div class="rectangle-3"></div>
    <div class="rectangle-4"></div>
    <div class="rectangle-5"></div>
    <div class="rectangle-6"></div>
    <div class="rectangle-5"></div>
    <div class="rectangle-4"></div>
    <div class="rectangle-3"></div>
    <div class="rectangle-2"></div>
    <div class="rectangle-1"></div> 
  </div>
{/if}




