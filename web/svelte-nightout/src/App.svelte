<script>
import Action from "./Action.svelte";
import Mechanic from "./Mechanic.svelte";
import Factory from "./Factory.svelte";
import Header from "./Header.svelte";
import { dAction, Vendor } from './Core';
import { Spinner } from 'sveltestrap';
import { onMount } from "svelte";
import { FridayAPI } from "./FridayAPI.js"

export let title = "Friday";


// States for our mechanic
let displayMechanic = false; // Render y/n
let dActionAtMech = null;    // daction to fix


// States for our actions
let displayActions = false; // Render y/n
let dActions = [];           // all dactions


// The 'App' exposes 4 things.
// 1. It exposes a way to 'remove' actions
// 2. It exposes a way to 'add' actions 
// 3. It exposes a way to 'modify' actions 
// 4. It exposes a way to sync with friday
// These things are represented by the functions below

// Currently removing and syncing is O(n) n: num actions
// I believe this will be fine

export let removeAction = dActionClicked => {
  // Removes the action
  dActions = dActions.filter(elem => elem.id != dActionClicked.id);

  // Syncs with friday
  if (dActionClicked.vendor == Vendor.hueLights) {
    FridayAPI.setHueLightsCommands(dActions);
  } else if (daction != undefined) {
    console.log("No vendor implemented for", daction.vendor)
  } else { }
}

export let addAction = () => {
  dActions.push(dAction.New());

  // force re-render
  dActions = dActions
}

export let showMechanic = dActionClicked => {
  dActionAtMech = dActionClicked
  displayMechanic = true;
}

export let syncFriday = daction => {
  if (daction.vendor == Vendor.hueLights) {
    FridayAPI.setHueLightsCommands(dActions);
  } else {
    console.log("No vendor implemented for", daction.vendor)
  }
}


onMount (async () => { 
  // Javascript is weird
  // basically push takes *args and we unfold the entire list as args
  // Also this only works for lists up to about 1e5 elements.. 
  dActions.push(... await FridayAPI.fetchActions());

  title = await FridayAPI.getDeviceName();

  // And then we display them
  displayActions = true;


  // TODO While developing mechanic
  /*dActionAtMech = dActions[0];*/
  /*displayMechanic = true;*/


});



</script>

<main>
  <Header title="{title}"/>

  {#if displayActions}
    {#each dActions as action (action.id)}
      <Action action={action} 
              bind:this={action.component}
              onKeywordClick={showMechanic}
              onCommandClick={showMechanic}
              onRemoveClick={removeAction}
              />
    {/each}
  {:else}
    <div class="middle-screen">
      <Spinner info type="grow" />
    </div>
  {/if}

  <Factory bind:active={displayActions} onAddClick={addAction}/>
  <Mechanic sync={syncFriday} daction={dActionAtMech} bind:active={displayMechanic} />
</main>

<style>
:global(body, html) {
  font-family: 'Lato', sans-serif;
  background-color: #080a10;
  color: #dfe6e9;
}



main {
  text-align: center;
  padding: 1em;
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


</style>
