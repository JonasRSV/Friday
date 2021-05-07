<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js"


export let page;
export let bottom;

// Code executed on variable updates
$: {



}

onMount (async () => { 
});



</script>

<style>

.button {
  height: 80px;
  border: none;
}

.button:disabled {
  background-color: #ff6f00;
}

.button:disabled:hover  {
  cursor: not-allowed;
}


.commands {
  background: url("/assets/icons/command-navbar-icon.svg");
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  
}

.keywords {
  background: url("/assets/icons/keyword-navbar-icon.svg") no-repeat;
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
}

</style>

{#if bottom}
  <nav class="fixed-bottom nav d-flex flex-row">
  {#if page == navigation.commands}
    <button class="commands button col-6" disabled> </button>
  {:else}
    <button class="commands button col-6" on:click={() => page = navigation.commands}> </button>
  {/if}
  

  {#if page == navigation.keywords}
    <button class="keywords button col-6" disabled> </button>
  {:else}
    <button class="keywords button col-6" on:click={() => page = navigation.keywords}> </button>
  {/if}

</nav>
{:else}
  <nav class="nav d-flex flex-row">
  {#if page == navigation.commands}
    <button class="commands button col-6" disabled> </button>
  {:else}
    <button class="commands button col-6" on:click={() => page = navigation.commands}> </button>
  {/if}
  

  {#if page == navigation.keywords}
    <button class="keywords button col-6" disabled> </button>
  {:else}
    <button class="keywords button col-6" on:click={() => page = navigation.keywords}> </button>
  {/if}

</nav>

{/if}
