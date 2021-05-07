<script>
import { onMount } from "svelte";
import { fade } from 'svelte/transition';

/*import { FridayAPI } from "./FridayAPI.js"*/
import Main from "./components/Main.svelte";
import LoadingScreen from "./components/LoadingScreen.svelte";
import { initCommands } from "./core/Command.js";
import { initKeywords } from "./core/Keyword.js";

let renderComponent = false;
let component = Main;
let props = {}

let setComponent = (c, p) => {
  props = p;
  component = c;
};

props = {
  "setComponent": setComponent,
  "root": component
}

onMount (async () => { 
  initCommands().then(_ => {
    initKeywords().then(_ => {
      renderComponent = true;
    });
  });
});



</script>


<style>

:global(body, html) {
  background-color: white;
}

</style>

{#if renderComponent}
<div in:fade>
  <svelte:component this={component} {...props}/>
</div>
{:else}
<LoadingScreen />
{/if}



