
<script>
import { onMount } from "svelte";
import CommandEditorKeywords from "./edit/CommandEditorKeywords.svelte"
import CommandEditorScripts from "./edit/CommandEditorScripts.svelte"
/*import { FridayAPI } from "./FridayAPI.js"*/

// self reference
export let root;


// 
export let setComponent;

export let goBack;
export let command;

onMount (async () => { 

});



</script>

<style>


main {
  text-align: center;
  padding: 1em;
  margin: 0 auto;
}
</style>




<main>
  <header class="mb-5">
    <h1>
      {command.id}
    </h1>
  </header>

  <CommandEditorKeywords root={root} setComponent={setComponent} keyword={command.keyword}/>
  <CommandEditorScripts root={root} setComponent={setComponent} scripts={command.scripts}/>


  <button on:click={goBack}>done</button>

</main> 

