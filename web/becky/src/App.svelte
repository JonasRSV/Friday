<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/
import Main from "./components/Main.svelte";
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

</style>

{#if renderComponent}
<svelte:component this={component} {...props}/>
{:else}
  <div> loading.. </div>
{/if}



