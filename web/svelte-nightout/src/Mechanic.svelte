
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import {Col, Container, Row} from 'sveltestrap';
import { FridayAPI } from "./FridayAPI.js";
import Keywords from "./mechanic/Keywords.svelte";
import Banners from "./mechanic/Banners.svelte";


// This function syncs a daction to friday
export let sync;
// If this component is active or not
export let active;
// The current action we're tinkering on
export let daction;

let keywords = []

let control;
let controlActive = false;


// Function for deactivating the mechanic
let deactivate = () => { 
  control = null;
  controlActive = false;
  active = false
}

let updateKeyword = (keyword) => {

  // Update UI components
  daction.setKeyword(keyword);

  // To re-render current component
  daction = daction

  // Sync the action with friday
  sync(daction);

  console.log("Updated keyword");
}

let newKeyword = () => {
  console.log("Made new keyword..");
}

let onBannerClick = (controlComponent) => {
  console.log("Clicked banner")
  control = controlComponent;
  controlActive = true;
}


FridayAPI.getKeywords().then(kw => keywords = kw);




</script>


<style>



.fixed-above {
  position: fixed;
  width: 100%;
  height: 100%;
  background-color: rgba(5, 5, 5, 0.9);
  top: 0px;
  left: 0px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: scroll;
}



</style>

{#if active}
<div class="fixed-above" on:click={deactivate} >
<Container class=container-xs>
  <Row> 
    <Col xs=4 sm=4 md=4 lg=4>
      <Keywords 
         bind:activeKeyword={daction.keyword} 
         bind:keywords={keywords} 
         updateKeyword={updateKeyword} 
         newKeyword={newKeyword}/>
    </Col>
  <Col xs=8 sm=8 md=8 lg=8>
    {#if controlActive}
      <svelte:component this={control} daction={daction} sync={sync} />
    {:else}
      <Banners onBannerClick={onBannerClick}/>
    {/if}
  </Col>
  </Row>
</Container>
</div>
{/if}
