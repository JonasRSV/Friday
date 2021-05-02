<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/
import NavBar from "./NavBar.svelte"
import Commands from "./Commands.svelte"
import Keywords from "./Keywords.svelte"
import { navigation } from "../core/Enums.js"


export let setComponent;

let title = "Becky";
let page = navigation.keywords;




onMount (async () => { 
  console.log("Mounting app")

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
  <header>
    <h1>{title}</h1>
  </header>
  <NavBar bind:page={page} bottom />

  {#if page == navigation.commands}
    <Commands setComponent={setComponent}/>
  {:else if page == navigation.keywords}
    <Keywords setComponent={setComponent}/>
  {:else}
    <div>Unknown page {page}</div>
  {/if}

</main>

