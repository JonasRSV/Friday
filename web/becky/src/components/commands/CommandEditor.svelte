
<script>
import { onMount } from "svelte";
import ScriptBar from "./scripts/ScriptBar.svelte"
import ScriptPick from "./scripts/ScriptPick.svelte"

export let root;
export let setComponent;

export let goBack;
export let command;

onMount (async () => { 

});

let updateScripts = (nextScripts) => {
  command.scripts = nextScripts;

  setComponent(
    root,
    {
      "root": root,
      "setComponent": setComponent,
      "goBack": goBack,
      "command": command
    }
  );
}

let pickScripts = () => {
  setComponent(ScriptPick,
    {
      currentScripts: command.scripts,
      nextScripts: updateScripts
    });
}


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


</style>




<main>
  <header class="mb-5">
    <h1>
      {command.id}
    </h1>
  </header>

  <div class="d-flex flex-row">
    <h3 class="text-left col-6">scripts</h3>
    <div class="d-flex col-6 flex-row justify-content-end"> 
      <button class="button" on:click={pickScripts}> edit </button>
    </div>
  </div>
  <hr>


{#each command.scripts as script (script)}
  <ScriptBar script={script}/>
{/each}


<button on:click={goBack}>done</button>

</main> 

