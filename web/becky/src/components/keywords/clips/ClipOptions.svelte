<script>
import { onMount } from "svelte";
import { fly } from 'svelte/transition';
/*import { FridayAPI } from "./FridayAPI.js"*/

export let show;
export let clip;
export let remove;
export let play;


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
    z-index: 9999;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);
  }


  .options {
    color: white;
  }

  .middle-screen {
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }


</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{ y: 800, duration: 500 }}">
  <div class="middle-screen options">
    <header>
      <h3>
        {clip}
      </h3>
    </header>
      <div class="d-flex flex-row">
        <div class="col-6">
          <button on:click={() => play(clip)}>
            play
          </button>
        </div>
        <div class="col-6">
          <button on:click={() => remove(clip)}>
            remove
          </button>
        </div>
      </div>
      <button on:click={() => show=false}> done</button>
  </div>
</div>





