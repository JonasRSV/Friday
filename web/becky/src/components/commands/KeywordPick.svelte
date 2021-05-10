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
    bottom: 0;
    position: fixed;
    width: 100%;
    z-index: 9998;

    background-color: #303841;

    display: flex;
    flex-direction: column;


  }


   /* Hide scrollbar for Chrome, Safari and Opera */


.bar {
  height: 70px;
  width: 100%;

  background-color: #3a4750;
  color: #eeeeee;
  border: none;

  -webkit-box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15); 
  box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15);
}

.bar:hover {
  opacity: 0.8;
  cursor: pointer;
}

.vertical {
  height: 100%;
}

.quit-bar {
  z-index: 9999;
  width: 100%;
  height: 100px;
  background-color: #303841;
}


.voice-bar {
  z-index: 9999;
  width: 100%;
  height: 80px;
  background-color: #303841;
}

.button-cancel {
  border: solid 3px #ff6f00;
  background-color: rgba(0, 0, 0, 0);
  background: url("/assets/icons/keyword-name-cancel.svg") no-repeat;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 10px;
  border-radius: 10px;

  height: 72px;
  width: 140px;

}

.icon-voice {
  background-color: rgba(0, 0, 0, 0);
  background: url("/assets/icons/voice-icon-orange.svg") no-repeat;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 10px;
  border-radius: 10px;

  height: 72px;
  width: 140px;

}

.vertical {
  height: 100%;
}

.keywords-container {
  height: 100%;
  overflow: scroll;

  -ms-overflow-style: none;  
  scrollbar-width: none;  
}

.keywords-container::-webkit-scrollbar {
  display: none;
}

</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{y: 800, duration: 500}}">

  <div class="voice-bar d-flex flex-direction-row justify-content-center">
    <div class="vertical d-flex flex-column justify-content-center">
      <div class="icon-voice"> </div>
    </div>
  </div>

  <div class="keywords-container">
    {#each pickableKeywords as keyword (keyword)}
      <button class="bar mb-3 shadow rounded text-center d-flex justify-content-center" 
        on:click={() => newCommand(keyword)}>
        <div class="vertical d-flex flex-column justify-content-center">
          <h2 class="vertical d-flex flex-column justify-content-center">
            {keyword}
          </h2>
        </div>
      </button>
    {/each}
  </div>

  <div class="quit-bar d-flex flex-direction-row justify-content-center">
    <div class="vertical d-flex flex-column justify-content-center">
      <button class="button-cancel" on:click={goBack}> </button>
    </div>
  </div>

</div>







