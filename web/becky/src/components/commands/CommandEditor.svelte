
<script>
import { onMount } from "svelte";
import ScriptBar from "./scripts/ScriptBar.svelte";
import ScriptPick from "./scripts/ScriptPick.svelte";
import CommandTrippleDotOption from "./CommandTrippleDotOption.svelte";
import { commands } from "../../core/Command.js";
import { FridayAPI } from "../../FridayAPI.js";

export let root;
export let setComponent;

export let goBack;
export let removeCommand;

export let keyword;
export let scripts;


let showTrippleDotOption = false;
onMount (async () => { 
  /*pickScripts();*/

});

let updateScripts = (nextScripts) => {
  scripts = nextScripts;
  commands[keyword] = nextScripts;

  // Update assistant
  FridayAPI.setBoundScripts(commands);

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

let remove = () => {
  toggleTrippleDot();
  removeCommand();
}


</script>

<style>


main {
  position: fixed;
  height: 100%;
  width: 100%;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  text-align: center;
  padding: 1em;
  margin: 0 auto;
}


.button {
  display: flex;
}

.tripple-dot {
  background: url("/assets/icons/meatball.svg");
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 10px;
  position: fixed;
  top: 15px;
  right: 10px;
  height: 60px;
  width: 40px;
  border: none;
  
}

.tripple-dot:focus {
  outline: none;
}

.goback-icon {
  position: fixed;
  top: 35px;
  left: 20px;

  height: 60px;
  width: 60px;

  background: url("/assets/icons/keyword-editor-goback.svg");
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  z-index: 10;

  border: none;
}

.edit-button {

  height: 60px;
  width: 60px;

  background: url("/assets/icons/edit.svg");
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  z-index: 10;

  border: none;

}

.keyword-header {
  max-width: 50%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-bottom {
  left: 0;
  bottom: 0;
  position: absolute;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: end;
  margin-block-start: 0;
  margin-block-end: 0;
}

.scripts-header {
  position: relative;
}
     
.scripts-container {
  height: 80%;

  overflow: scroll;

  -ms-overflow-style: none;  
  scrollbar-width: none;  

}

.scripts-container::-webkit-scrollbar {
  display: none;
}

.dummy {
  height: 100px;
}

</style>




<main>
  <button class="goback-icon" on:click={goBack}></button>  

  {#if showTrippleDotOption}
    <CommandTrippleDotOption name={keyword} goBack={toggleTrippleDot} 
    remove={remove}/>
  {/if}

  <header class="mb-5 d-flex flex-row justify-content-center">
    <h1 class="keyword-header"> {keyword} </h1>
  </header>

  <button class="tripple-dot" on:click={toggleTrippleDot}> </button>


  <div class="scripts-header d-flex flex-row justify-content-end">
    <h3 class="text-left text-bottom">scripts</h3>
    <div class="d-flex col-6 flex-row justify-content-end"> 
      <button class="edit-button button" on:click={pickScripts}> </button>
    </div>
  </div>
  <hr>


  <div class="scripts-container pb-5">
    {#each scripts as script (script)}
      <ScriptBar script={script}/>
    {/each}
    <div class="dummy"> </div>
  </div>

</main>


