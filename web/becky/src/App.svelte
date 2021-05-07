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
  background-color: #303841;
  color: #eeeeee;
  font-family: Helvetica;
  font-family:Cambria,
}

:global(h1) {
  font-family: Helvetica;
  font-size: 39px;
  font-weight: 700;
}

:global(h2) {
  font-size: 31px;
}

:global(h3) {
  font-size: 25px;
}

:global(h4) {
  font-size: 20px;
}

:global(p) {
  font-size: 16px;
}

:global(h2, h3, h4, p) {
  font-family: Cambria;
  font-weight: 700;
}

</style>

{#if renderComponent}
<div in:fade>
  <svelte:component this={component} {...props}/>
</div>
{:else}
<LoadingScreen />
{/if}



