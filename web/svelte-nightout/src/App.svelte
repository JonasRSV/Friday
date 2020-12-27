<script>
import Action from "./Action.svelte";
import ActionModifier from "./ActionModifier.svelte";
import Header from "./Header.svelte";
import { Spinner } from 'sveltestrap';
import { onMount } from "svelte";

import { dManager } from "./dManager.js";
import { API } from "./FridayAPI.js"

export let title = "Friday";


// Different view states
let display_modifier = false;
let display_actions = false;

// All rendered dActions
let dactions = [];

let manager = new dManager();
let api = new API(manager);


export let onNameClick = () => {
  console.log("Clicked on name");

};


export let onCommandClick = () => {
  console.log("Clicked on command");
};


onMount (async () => { 
  await api.fetch_actions()

  // After fetching actions we display them.
  dactions = manager.get_actions();
  display_actions = true;
});

setTimeout(() => {
  dactions[0].component.updateName("Cookie");

}, 5000);


</script>

<main>
  <Header title="{title}"/>
  {#if display_modifier}
    <ActionModifier action="hi" />
  {:else if display_actions}
    {#each dactions as action (action.id)}
      <Action action={action} 
              bind:this={action.component}
              onNameClick={onNameClick}
              onCommandClick={onCommandClick}/>
      <div class="empty-space"> </div>
    {/each}
  {:else}
    <div class="middle-screen">
      <Spinner info type="grow" />
    </div>
  {/if}
</main>

<style>
:global(body, html) {
  background-color: #080a10;
  color: #dfe6e9;
}
main {
  text-align: center;
  padding: 1em;
  max-width: 240px;
  margin: 0 auto;
}


.middle-screen {
  position: fixed;
  margin: 0 auto;
  top: 50%;
  left: 50%;

  /*To truly get it into the center*/
  transform: translate(-50%, -50%);
}

.empty-space {
  height: 80px;
}


@media (min-width: 640px) {
  main {
    max-width: none;
  }
}
</style>
