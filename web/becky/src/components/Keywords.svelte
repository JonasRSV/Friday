<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js";
import KeywordBar from "./keywords/KeywordBar.svelte";
import KeywordEditor from "./keywords/KeywordEditor.svelte";
import NameInput from "./keywords/NameInput.svelte";
import Add from "./Add.svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/


export let root;
export let setComponent;
export let onKeywordClick = (keyword, clips) => {
  // Update our display component to the command editor and set
  // the proper 'goBack' function
  setComponent(
    KeywordEditor, {
      // update to new root
      "root": KeywordEditor,
      "setComponent": setComponent,
      goBack:  () => setComponent(
        root, {
          page: navigation.keywords,
          "root": root,
          "setComponent": setComponent
        }
      ), 
      "keyword": keyword,
      "clips": clips,
      "syncFriday": syncFriday
    }
  );
};

// If true, it is possible to add keywords in this window
export let addable = true;


let getName = false;

let keywords = {}

// Sync keywords to Friday 
let syncFriday = () => {
  console.log("syncing to friday model..");
  console.log("syncing", keywords);
  let syncingPromise = new Promise((resolve, _) => {
    setTimeout(() => {
      resolve("ok");
    }, 1000);
  });

  return syncingPromise;
}

let addClick = () => getName = true;
let cancel = () => getName = false;
let addKeyword = (name) => {
  // Create empty keyword and jump into editor
  keywords[name] = []
  onKeywordClick(name, keywords[name]);
}




onMount (async () => { 
  keywords = {
      "hello": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],

      "hi": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],
      "whats up": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],
      "lights on": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],
      "lights off": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],
      "cookie time": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ],
      "good night": [
        "123-222-333-111.wav",
        "223-222-333-111.wav",
        "223-333-333-111.wav",
      ]
  }
});




</script>

<style>


</style>

{#each Object.entries(keywords) as [keyword, clips] (keyword)}
  <KeywordBar bind:keyword={keyword} click={() => onKeywordClick(keyword, clips)}/>
{/each}


{#if addable}
  <Add click={addClick} />
{/if}

{#if getName}
  <NameInput cancel={cancel} addKeyword={addKeyword} keywords={keywords} />
{/if}



