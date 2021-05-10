<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/
import NavBar from "./NavBar.svelte"
import Commands from "./Commands.svelte"
import Keywords from "./Keywords.svelte"
import { navigation } from "../core/Enums.js"
import { getName } from "../core/Device.js"
/*import { FridayAPI } from "../FridayAPI.js"*/

export let setComponent;
export let page = navigation.keywords;
export let root;

let title = getName();

onMount (async () => { 
  /*title = getName();*/
});



</script>

<style>

main {
  text-align: center;
  padding: 1em;
  margin: 0 auto;

  margin-bottom: 80px;

}


</style>


<main>
  <header class="mb-5">
    <h1>{title}</h1>
  </header>
  <NavBar bind:page={page} />
  {#if page == navigation.commands}
    <Commands setComponent={setComponent} root={root}/>
  {:else if page == navigation.keywords}
    <Keywords setComponent={setComponent} root={root}/>
  {:else}
    <div>Unknown page {page}</div>
  {/if}


</main>

