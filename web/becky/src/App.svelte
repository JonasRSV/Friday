<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/
import Main from "./components/Main.svelte"

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
});



</script>

<style>

</style>

<svelte:component this={component} {...props}/>



