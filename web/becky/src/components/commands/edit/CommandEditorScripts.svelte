<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

// self reference
export let root;
export let scripts;


// 
export let setComponent;


onMount (async () => { 


});



</script>

<style>


</style>



<p> Scripts <span> <button> edit </button> </span></p> 
<hr>

{#each scripts as script (script)}
  <div>{script}</div>
{/each}

