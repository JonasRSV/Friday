
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { FridayAPI } from "./FridayAPI.js";
import Keywords from "./mechanic/Keywords.svelte";
import Banners from "./mechanic/Banners.svelte";
import KeywordBuilder from "./mechanic/keywords/KeywordBuilder.svelte"
/*import Scripts from "./mechanic/scripts/Scripts.svelte"*/


// This function syncs a command to friday
export let sync;
// If this component is active or not
export let active;
// The current command we're tinkering on
export let command;


$: {
  keywordPickerActive = active;
}

let keywords = []

let control;
// If we are to render the control builder
let controlBuilderActive = false;

// If we are to render the controlPicker 
let controlPickerActive = false;

// If we are to render the keyword builder
let keywordBuilderActive = false;

// If we are to render the keyword picker
let keywordPickerActive = false;


// Function for deactivating the mechanic
let deActMechanic = () => { 
  active = false;
  controlBuilderActive = false;
  controlPickerActive = false;
  keywordBuilderActive = false;
  keywordPickerActive = false;
}

let deActControlBuilder = () => {
  controlBuilderActive = false;
  controlPickerActive = true;
}

let deActControlPicker = () => {
  controlPickerActive = false;
  keywordPickerActive = true;
}

let deActKeywordBuilder = () => {
  keywordBuilderActive = false;
  keywordPickerActive = true;

  // fetch new updated keywords
  FridayAPI.getKeywords().then(server_keywords => keywords = server_keywords);
}

let deActKeywordPicker = () => {
  keywordPickerActive = false;

  deActMechanic();
}


let actControlPicker = () => {
  controlPickerActive = true;
}

let actKeywordBuilder = () => {
  keywordBuilderActive = true;
}

let actKeywordPicker = () => {
  keywordPickerActive = true;
}

let updateKeyword = (keyword) => {

  // Update UI components
  command.setKeyword(keyword);

  // To re-render current component
  command = command

  // Sync the action with friday
  sync(command);

  // Control Picker
  controlPickerActive = true;
  keywordPickerActive = false;
}

let onBannerClick = (controlComponent) => {
  control = controlComponent;
  controlBuilderActive = true;
}


FridayAPI.getKeywords().then(server_keywords => keywords = server_keywords);




</script>


<style>



.fixed-above {
  position: fixed;
  width: 100%;
  height: 100%;
  background-color: rgba(5, 5, 5, 0.97);
  top: 0px;
  left: 0px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: scroll;
}



</style>

{#if active}
  {#if keywordBuilderActive}
    <div class="fixed-above" on:click={deActKeywordBuilder}>
      <KeywordBuilder deactivate={deActKeywordBuilder}/>
    </div>
  {:else if keywordPickerActive}
    <div class="fixed-above" on:click={deActKeywordPicker}>
      <Keywords 
         bind:activeKeyword={command.keyword} 
         bind:keywords={keywords} 
         updateKeyword={updateKeyword} 
         newKeyword={actKeywordBuilder}/>
    </div>
  {:else if controlBuilderActive}
    <div class="fixed-above" on:click={deActMechanic}>
      <svelte:component this={control} command={command} sync={sync} deactivate={deActMechanic}/>
    </div>
  {:else if controlPickerActive}
    <div class="fixed-above" on:click={deActControlPicker}>
        <Banners onBannerClick={onBannerClick}/>
    </div>
  {:else}
    <h1> Error </h1>
  {/if}
{/if}
