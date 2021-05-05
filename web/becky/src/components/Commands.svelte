<script>
import { onMount } from "svelte";
import { Command } from "../core/Command.js";
import { navigation } from "../core/Enums.js";
import CommandBar from "./commands/CommandBar.svelte";
import CommandEditor from "./commands/CommandEditor.svelte"
import Add from "./Add.svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/


export let root;
export let setComponent;

let commands = []


onMount (async () => { 

  // TODO: load from API
  commands = [
    new Command("hello", ["hi.py", "bye.py"]),
    new Command("good bye", ["goodbye.sh", "bye.sh"])
  ]


  // When editing commandEditor
 /*onCommandClick(commands[0]);*/

});

let onCommandClick = (c) => {
  // Update our display component to the command editor and set
  // the proper 'goBack' function
  setComponent(
    CommandEditor, {
      "root": CommandEditor,
      "setComponent": setComponent,
      goBack:  () => setComponent(
        root, {
          page: navigation.commands,
          "root": root,
          "setComponent": setComponent
        }
      ), 
      command: c
    }
  );

  console.log("Clicked on", c.id);

};

let addClick = () => {
  console.log("adding command");
}



</script>

<style>


</style>


{#each commands as command (command.id)}
  <CommandBar bind:command={command} click={() => onCommandClick(command)}/>
{/each}



<Add click={addClick} />

