<script>
import { onMount } from "svelte";
import { keywords } from "../../core/Keyword.js";
import { commands } from "../../core/Command.js";
import { fly } from 'svelte/transition';
/*import { FridayAPI } from "./FridayAPI.js"*/


export let newCommand;
export let goBack;


let pickableKeywords = [];

onMount (async () => { 
  let canPick = [];

  for (var keyword of Object.keys(keywords)) {
    if (! (keyword in commands)) {
      canPick.push(keyword); 
    }
  }

  pickableKeywords = canPick;

});



</script>

<style>
  .layover {
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    display: flex;
    flex-direction: row;
    justify-content: center;
    height: 100%;
    width: 100%;
    z-index: 9999;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);
  }


  .options {
    color: white;
  }

  .middle-screen {
    width: 80%;
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }


.bar {
  height: 70px;
  width: 100%;
  background-color: white;
}

.bar:hover {
  opacity: 0.8;
  cursor: pointer;
}

.vertical {
  height: 100%;
}


</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{y: 800, duration: 500}}">
  <div class="middle-screen options">
      {#each pickableKeywords as keyword (keyword)}
        <button class="bar mb-3 shadow rounded text-center d-flex justify-content-center" 
          on:click={() => newCommand(keyword)}>
          <div class="vertical d-flex flex-column justify-content-center font-weight-light ">
            {keyword}
          </div>
        </button>

      {/each}

      <button on:click={goBack}> done</button>
  </div>
</div>





