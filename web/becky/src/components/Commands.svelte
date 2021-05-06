<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js";
import CommandBar from "./commands/CommandBar.svelte";
import CommandEditor from "./commands/CommandEditor.svelte"
import { commands } from "../core/Command.js";
import Add from "./Add.svelte";
import KeywordPick from "./commands/KeywordPick.svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/


export let root;
export let setComponent;

let renderedCommands = []
let pickKeyword = false;

// TODO: load from API onMount

onMount (async () => { 
  renderedCommands = commands;


  // When editing commandEditor
 /*onCommandClick(commands[0]);*/

});


let onCommandClick = (keyword, scripts) => {
  // Update our display component to the command editor and set
  // the proper 'goBack' function
  setComponent(
    CommandEditor, {
      "root": CommandEditor,
      "setComponent": setComponent,
      "removeCommand": () => {
        delete commands[keyword];

        /*TODO: Remove from Friday*/
        console.log("commands", commands);

        setComponent(
          root, {
            page: navigation.commands,
            "root": root,
            "setComponent": setComponent,
        })
      },
      goBack:  () => setComponent(
        root, {
          page: navigation.commands,
          "root": root,
          "setComponent": setComponent,
        }
      ), 
      "keyword": keyword,
      "scripts": scripts
    }
  );

  console.log("Clicked on", keyword);

};

let toggleKeywordPick = () => pickKeyword = !pickKeyword;

let addCommand = (keyword) => {
  toggleKeywordPick();

  commands[keyword] = [];

  onCommandClick(keyword, commands[keyword]);
}




</script>

<style>


</style>

{#each Object.entries(renderedCommands) as [keyword, scripts] (keyword)}
  <CommandBar keyword={keyword} click={() => onCommandClick(keyword, scripts)}/>
{/each}



<Add click={toggleKeywordPick} />

{#if pickKeyword}
  <KeywordPick goBack={toggleKeywordPick} newCommand={addCommand} />
{/if}
