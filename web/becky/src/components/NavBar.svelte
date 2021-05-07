<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js"


export let page;

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

.commands-disabled {
  background: url("/assets/icons/cmd-icon-gray.svg");
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 15px;

}

.commands-enabled {
  background: url("/assets/icons/cmd-icon-orange.svg");
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 15px;

}

.keywords-disabled {
  background: url("/assets/icons/voice-icon-gray.svg");
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 15px;

}

.keywords-enabled {
  background: url("/assets/icons/voice-icon-orange.svg");
  background-color: #3a4750;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 15px;
}

</style>

<nav class="fixed-bottom nav d-flex flex-row">
{#if page == navigation.commands}
  <button class="commands-disabled button col-6" disabled> </button>
{:else}
  <button class="commands-enabled button col-6" on:click={() => page = navigation.commands}> </button>
{/if}


{#if page == navigation.keywords}
  <button class="keywords-disabled button col-6" disabled> </button>
{:else}
  <button class="keywords-enabled button col-6" on:click={() => page = navigation.keywords}> </button>
{/if}

</nav>
