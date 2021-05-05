<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

// list of current scripts
export let currentScripts;

// function taking list of next scripts
export let nextScripts;



// list of all scripts
let scripts = []

onMount (async () => { 
  scripts = {
    "hi.py": currentScripts.includes("hi.py"), 
    "bye.py": currentScripts.includes("bye.py"),
    "hello.sh": currentScripts.includes("hello.sh"),
    "kalle.sh": currentScripts.includes("kalle.sh")
  }
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




</script>

<style>

.bar {
  height: 70px;
  width: 100%;
  background-color: white;
}


</style>


{#each Object.entries(scripts) as [script, active] (script)}
  <div class="d-flex bar shadow flex-row">
    <div class="col-6"> {script} </div>
    <div class="d-flex col-6 flex-row justify-content-end">
      {#if active}
        <input type="checkbox" checked on:click={() => scripts[script] = false}>
      {:else}
        <input type="checkbox" on:click={() => scripts[script] = true}>
      {/if}
    </div>
  </div>
{/each}


<button on:click={donePicking}> done </button>



