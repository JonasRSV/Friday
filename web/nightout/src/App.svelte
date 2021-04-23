<script>
import CommandWidget from "./CommandWidget.svelte";
import Mechanic from "./Mechanic.svelte";
import AddCommandButton from "./action/AddCommandButton.svelte";
import Header from "./Header.svelte";
import { Spinner } from 'sveltestrap';
import { onMount } from "svelte";
import { FridayAPI } from "./FridayAPI.js"
import { Command } from "./core/Command.js"

export let title = "Friday";


// States for our mechanic
let displayMechanic = false; // Render y/n
let renderCommands = false; // Render y/n

let commands = []; // all commands the assistant knows
let commandAtMechanic = null;    // command to fix


// The 'App' exposes 4 things.
// 1. It exposes a way to 'remove' commands
// 2. It exposes a way to 'add' commands 
// 3. It exposes a way to 'modify' commands 
// 4. It exposes a way to sync with friday
// These things are represented by the functions below

let commandsToScripts = () => {
  let scripts = {}
  commands.forEach(command => {
    scripts[command.keyword] = command.scripts;
  });

  return scripts;
  
}

let syncFriday = () => FridayAPI.setBoundScripts(commandsToScripts(commands));

let removeCommand = command => {
  // Removes the action
  commands = commands.filter(elem => elem.id != command.id);

  // Syncs with friday
  syncFriday();

  // re-render
  commands = commands
}

let addCommand = () => {
  commands.push(Command.New());

  // force re-render
  commands = commands
}

let showMechanic = command => {
  commandAtMechanic = command
  displayMechanic = true;
}



onMount (async () => { 
  let scripts = await FridayAPI.getBoundScripts();

  for (var key in scripts) {
    commands.push(new Command(key, scripts[key]));
  }

  title = await FridayAPI.getDeviceName();
  // And then we display them
  renderCommands = true;


  // TODO While developing mechanic
  commandAtMechanic = commands[0];
  displayMechanic = true;


});



</script>

<main>
  <Header title="{title}"/>
  {#if renderCommands}
    {#each commands as command (command.id)}
      <CommandWidget command={command} 
              bind:this={command.component}
              openMechanic={showMechanic}
              onRemoveClick={removeCommand}
              />
    {/each}
  {:else}
    <div class="middle-screen">
      <Spinner info type="grow" />
    </div>
  {/if}

  <AddCommandButton bind:active={renderCommands} onAddClick={addCommand}/>
  <Mechanic sync={syncFriday} command={commandAtMechanic} bind:active={displayMechanic} />
</main>

<style>
:global(body, html) {
  font-family: 'Lato', sans-serif;
  background-color: #080a10;
  color: #dfe6e9;
}

:global(.full-height) {
  height: 100%;
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
