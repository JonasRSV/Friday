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
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    height: 100%;
    width: 100%;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);
  }


  .options {
    color: white;
    width: 100%;
    right: 0;
    left: 0;
  }

  .middle-screen {
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }

  .button {
    height: 80px;
  }


</style>

<div class="layover">
  <div class="middle-screen options">
    <header>
      <h3>
        {clip}
      </h3>
    </header>
    <div class="d-flex flex-row">
      <button class="button col-6" on:click={() => retry(clip)}> retry </button>
      <button class="button col-6" on:click={() => play(clip)}> play </button>
    </div>
    <div class="d-flex flex-row">
      <button class="button col-6" on:click={() => remove(clip)}> remove </button>
      <button class="button col-6" on:click={accept}> accept </button>
    </div>
  </div>
</div>





