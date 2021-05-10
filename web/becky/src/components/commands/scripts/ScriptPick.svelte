<script>
import { onMount } from "svelte";
import { FridayAPI } from "../../../FridayAPI.js";
/*import { FridayAPI } from "./FridayAPI.js"*/

// list of current scripts
export let currentScripts;

// function taking list of next scripts
export let nextScripts;



// list of all scripts
let scripts = {}

onMount (async () => { 
  FridayAPI.getAllScripts().then(allScripts => {
    allScripts.forEach(script => {
      scripts[script] = currentScripts.includes(script);
    });
  });
});


let donePicking = () => {
  let next = []
  for (const [script, active] of Object.entries(scripts)) {
    if (active) {
      next.push(script);
    }
  }

  nextScripts(next);
};


let toggle = (script) => {
  scripts[script] = !scripts[script]
}




</script>

<style>

.bar {
  height: 70px;
  width: 100%;

  background-color: #3a4750;
  color: #eeeeee;
  border: none;

  -webkit-box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15); 
  box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15);
}


.keyword-header {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;

}

main {
  padding: 1em;

}

.scroller {
  overflow: scroll;
  height: 100%;
  -ms-overflow-style: none;  
  scrollbar-width: none;  

}

.scroller::-webkit-scrollbar {
  display: none;
}

.title {
  padding: 1em;
}

.button-done {
  background: url("/assets/icons/keyword-name-ok.svg") no-repeat;
  background-color: #ff6f00;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  border-radius: 10px;

  border: none;
  height: 72px;
  width: 140px;
}

.done-bar {
  z-index: 9999;
  width: 100%;
  height: 130px;
  background-color: #303841;
}

.title-bar {
  z-index: 9999;
  width: 100%;
  height: 130px;
  background-color: #303841;
}

.vertical {
  height: 100%;
}

.check-box {
  height: 25px;
  width: 25px;

}

main {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

</style>

<main class="d-flex flex-column">

  <div class="title-bar d-flex flex-direction-row justify-content-center">
    <div class="vertical d-flex flex-column justify-content-center">
      <div class="title">
        <header class="mb-5 d-flex flex-row justify-content-center">
          <h1 class="keyword-header">Scripts</h1>
        </header>
      </div>
    </div>
  </div>

  <div class="scroller">

    {#each Object.entries(scripts) as [script, active] (script)}
      <div class="d-flex bar shadow flex-row mb-3 mt-3" on:click={() => toggle(script)}>
        <div class="col-6 d-flex flex-column justify-content-center"> 
          <h2>
            {script} 
          </h2>
        </div>
        <div class="d-flex col-6 flex-row justify-content-end">
          <div class="vertical d-flex flex-column justify-content-center" on:click={(e) => e.stopPropagation()} >
            {#if active}
              <input class="check-box" type="checkbox" checked on:click={() => scripts[script] = false}>
            {:else}
              <input class="check-box" type="checkbox" on:click={() => scripts[script] = true}>
            {/if}
          </div>
        </div>
      </div>
    {/each}


  </div>


  <div class="done-bar d-flex flex-direction-row justify-content-center">
    <div class="vertical d-flex flex-column justify-content-center">
      <button class="button-done" on:click={donePicking}> </button>
    </div>
  </div>


</main>








