
<script>
import { onMount } from "svelte";
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


</style>




<button on:click={goBack}>{command.id}</button>

