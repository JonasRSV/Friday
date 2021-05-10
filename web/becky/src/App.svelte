<script>
import { onMount } from "svelte";
import { fade } from 'svelte/transition';

/*import { FridayAPI } from "./FridayAPI.js"*/
import Main from "./components/Main.svelte";
import LoadingScreen from "./components/LoadingScreen.svelte";
import { initCommands } from "./core/Command.js";
import { initKeywords } from "./core/Keyword.js";
import { initDevice } from "./core/Device.js";

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
      initDevice().then(_ => {
        // ugly fix for some race condition
        setTimeout(() => renderComponent = true, 500);
      });
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
  margin-top: 25px;
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
<div in:fade class="main">
  <svelte:component this={component} {...props}/>
</div>
{:else}
<LoadingScreen />
{/if}



