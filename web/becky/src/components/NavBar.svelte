<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js"


export let page;
export let bottom;

// Code executed on variable updates
$: {



}

onMount (async () => { 
  console.log("Mounting app")

});



</script>

<style>

.button {
  height: 80px;
}

.button:disabled {
  background-color: green;
}

.button:disabled:hover  {
  cursor: not-allowed;
}


.commands {
  background: url("/assets/icons/command-window.svg");
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
  
}

.keywords {
  background: url("/assets/icons/voice-message.svg") no-repeat;
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
