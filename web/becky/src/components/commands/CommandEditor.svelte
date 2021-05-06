
<script>
import { onMount } from "svelte";
import ScriptBar from "./scripts/ScriptBar.svelte";
import ScriptPick from "./scripts/ScriptPick.svelte";
import CommandTrippleDotOption from "./CommandTrippleDotOption.svelte";
import { commands } from "../../core/Command.js";

export let root;
export let setComponent;

export let goBack;
export let removeCommand;

export let keyword;
export let scripts;


let showTrippleDotOption = false;
onMount (async () => { 

});

let updateScripts = (nextScripts) => {
  scripts = nextScripts;
  commands[keyword] = nextScripts;

  setComponent(
    root,
    {
      "root": root,
      "setComponent": setComponent,
      "goBack": goBack,
      "keyword": keyword,
      "scripts": scripts,
      "removeCommand": removeCommand
    }
  );
}

let pickScripts = () => {
  setComponent(ScriptPick,
    {
      currentScripts: scripts,
      nextScripts: updateScripts
    });
}

let toggleTrippleDot = () => showTrippleDotOption = !showTrippleDotOption;


</script>

<style>


main {
  text-align: center;
  padding: 1em;
  margin: 0 auto;
}


.button {
  display: flex;
}

.tripple-dot {
  background: url("/assets/icons/three-dot-command-icon.svg");
  background-color: white;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  position: fixed;
  top: 0;
  right: 5px;
  height: 60px;
  width: 40px;
  border: none;
  
}


</style>




<main>
  <header class="mb-5">
    <h1>
      {keyword}
    </h1>
  </header>

  <button class="tripple-dot" on:click={toggleTrippleDot}> 
  </button>


  <div class="d-flex flex-row">
    <h3 class="text-left col-6">scripts</h3>
    <div class="d-flex col-6 flex-row justify-content-end"> 
      <button class="button" on:click={pickScripts}> edit </button>
    </div>
  </div>
  <hr>


{#each scripts as script (script)}
  <ScriptBar script={script}/>
{/each}

<button on:click={goBack}>done</button>
</main> 

{#if showTrippleDotOption}
  <CommandTrippleDotOption goBack={toggleTrippleDot} 
  remove={removeCommand}/>
{/if}

