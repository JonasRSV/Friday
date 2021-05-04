<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let clip;


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

<div class="layover">
  <div class="middle-screen options">
    <header>
      <h3>
        {clip}
      </h3>
    </header>
      <div class="d-flex flex-row">
        <div class="col-6">
          <button>
            play
          </button>
        </div>
        <div class="col-6">
          <button>
            remove
          </button>
        </div>
      </div>
      <button on:click={() => clip=null}> done</button>
  </div>
</div>





