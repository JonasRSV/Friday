<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/
import Main from "./components/Main.svelte"

let component = Main;
let props = {}
let setComponent = (c, p) => {
  console.log("component", c, "props", p)
  props = p;
  component = c;
};

onMount (async () => { 
  console.log("Mounting app")
});



</script>

<style>

</style>

<svelte:component this={component} root={component} setComponent={setComponent} {...props}/>



