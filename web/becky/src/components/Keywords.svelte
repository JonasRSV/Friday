<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js";
import { keywords, keywordSync } from "../core/Keyword.js";
import KeywordBar from "./keywords/KeywordBar.svelte";
import KeywordEditor from "./keywords/KeywordEditor.svelte";
import NameInput from "./keywords/NameInput.svelte";
import Add from "./Add.svelte";


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
let renderedKeywords = {}

// Sync keywords to Friday 
let syncFriday = (keyword, clips) => {
  if (clips.length == 0) {
    delete keywords[keyword];
  } else {
    keywords[keyword] = clips;
  }
  
  let syncingPromise = keywordSync();

  return syncingPromise;
}

let toggleGetName = () => getName = !getName;

let addKeyword = (name) => {
  toggleGetName();
  // Create empty keyword and jump into editor
  keywords[name] = []
  onKeywordClick(name, keywords[name]);
}




onMount (async () => { 
  // Clean up any empty keywords since they are not persisted on the assistant
  // anyway.
  for (var [keyword, clips] of Object.entries(keywords)) {
    if (clips.length == 0) {
      delete keywords[keyword];
    }
  }

  renderedKeywords = keywords;
  /*onKeywordClick("good", keywords["good"])*/
});




</script>

<style>


</style>

{#each Object.entries(renderedKeywords) as [keyword, clips] (keyword)}
  <KeywordBar bind:keyword={keyword} click={() => onKeywordClick(keyword, clips)}/>
{/each}


{#if addable}
  <Add click={toggleGetName} />
{/if}

{#if getName}
  <NameInput cancel={toggleGetName} addKeyword={addKeyword} keywords={keywords} />
{/if}



