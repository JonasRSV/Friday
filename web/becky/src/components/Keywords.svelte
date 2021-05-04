<script>
import { onMount } from "svelte";
import { navigation } from "../core/Enums.js";
import KeywordBar from "./keywords/KeywordBar.svelte"
import KeywordEditor from "./keywords/KeywordEditor.svelte"
/*import { FridayAPI } from "./FridayAPI.js"*/


export let root;
export let setComponent;

let keywords = []



onMount (async () => { 
  keywords = [
    "hello",
    "hi",
    "whats up",
    "lights on",
    "lights off",
    "cookie time",
    "good night"
  ]

  /*onKeywordClick("lights on");*/



});

let onKeywordClick = (keyword) => {
  // Update our display component to the command editor and set
  // the proper 'goBack' function
  setComponent(
    KeywordEditor, {
      goBack:  () => setComponent(
        root, {
          page: navigation.keywords
        }
      ), 
      "keyword": keyword
    }
  );

  console.log("Clicked on", keyword);

};



</script>

<style>


</style>

{#each keywords as keyword (keyword)}
  <KeywordBar bind:keyword={keyword} click={() => onKeywordClick(keyword)}/>
{/each}





