<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/


export let clip;

// Play the recording
export let play;

// retry same recording 
export let retry;

// accept all recordings
export let accept;

// stop recording flow and discard all
export let remove;


onMount (async () => { 


});



</script>

<style>
  .layover {
    z-index: 500;
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    height: 100%;
    width: 100%;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);
  }


  .options {
    padding-bottom: 25px;
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 25px;
    color: white;
    width: 90%;
    right: 10%;
    left: 10%;

    background-color: #3a4750;
    border-radius: 10px;
  }

  .middle-screen {
    width: 100%;
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }

  .button {
    height: 80px;
    width: 100%;
    border-radius: 10px;
  }

  .button-container {
    padding: 12px;
  }

  .retry-button {
    border: none;

    background: url("/assets/icons/keyword-name-ok.svg");
    background-color: #ff6f00;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 10px; 
    z-index: 10;

  }

  .play-button {
    border: none;

    background: url("/assets/icons/play.svg");
    background-color: #ff6f00;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 10px; 
    z-index: 10;

  }

  .remove-button {
    border: none;

    background: url("/assets/icons/trashcan.svg");
    border: solid 3px #ff6f00;
    background-color: #3a4750;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 10px; 
    z-index: 10;

  }

  .accept-button {
    border: none;

    background: url("/assets/icons/keyword-name-ok.svg");
    background-color: #ff6f00;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 10px; 
    z-index: 10;
  }


</style>

<div class="layover">
  <div class="middle-screen d-flex flex-row justify-content-center">
    <div class="options">
      <header>
        <h3>
          {clip}
        </h3>
      </header>
      <div class="grid p-2">
        <div class="d-flex flex-row" >
          <div class="col-6 button-container">
            <button class="button retry-button" on:click={() => retry(clip)}> </button>
          </div>
          <div class="col-6 button-container">
            <button class="button play-button" on:click={() => play(clip)}> </button>
          </div>
        </div>
        <div class="d-flex flex-row">
          <div class="col-6 button-container">
            <button class="button remove-button" on:click={() => remove(clip)}> </button>
          </div>
          <div class="col-6 button-container">
            <button class="button accept-button" on:click={accept}> </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>





