<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row } from 'sveltestrap';
import FaRegPlusSquare from 'svelte-icons/fa/FaRegPlusSquare.svelte'
import CogsBanner from "./../banners/CogsBanner.svelte"
import GreenCogsBanner from "./../banners/GreenCogsBanner.svelte"

// Current active keyword
export let activeKeyword;

// Function to call on-change of active keyword
export let updateKeyword;

export let newKeyword;

// All keywords available
export let keywords = [];

let onActiveClick = (e) => e.stopPropagation();
let onInactiveClick = (e, keyword) => {
  e.stopPropagation();
  updateKeyword(keyword);
}

let onNewClick = (e) => {
  e.stopPropagation();
  newKeyword();
}

let keywordProperties = []
// Everything in this block is called on a change of our variables
$: {

  console.log("rerendering");
  keywordProperties = keywords.map(keyword => {
      return {
        "name": keyword,
        "active": keyword == activeKeyword,
      }
  })
}


</script>


<style>

.full-width {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: center;
}

.keyword {
  height: 50px;
  overflow: hidden;
  display: flex;
  flex-direction: column; 
  justify-content: center;
}

:global(.container-keywords) {
  overflow-y: scroll;
  overflow-x: visible;
}

.empty-space {
  height: 10px;
}

.horizontal-center {
  display: flex;
  flex-direction: row;
  justify-content: center;
  width: 100%;
}

.add-icon {
  width: 60px;
  height: 60px;
  color: #8A8A8A;
}

.add-icon:hover {
  cursor: pointer;
  opacity: 0.9;
}

.opacity-hover:hover {
  cursor: pointer;
  opacity: 0.8;
}

</style>


<Container fluid class="container-keywords">
{#each keywordProperties as keyword }
  {#if keyword.active}
    <GreenCogsBanner>
      <Row class="text-center"> 
        <div class="full-width" on:click={onActiveClick}>
          <div class="keyword active" > {keyword.name} </div>
        </div>
      </Row>
    </GreenCogsBanner>
  {:else}
    <div class="opacity-hover">
      <CogsBanner>
        <Row class="text-center"> 
          <div class="full-width"  on:click={(e) => onInactiveClick(e, keyword.name)}>
            <div class="keyword"> {keyword.name} </div>
          </div>
        </Row>
      </CogsBanner>
    </div>
  {/if}

  <div class="empty-space"></div>
{/each}

<div class="empty-space"></div>
<div class="empty-space"></div>

<Row class="text-center"> 
  <div class="horizontal-center">
    <div class="add-icon" on:click={onNewClick}>
      <FaRegPlusSquare/> 
    </div>
  </div>
</Row>

</Container>
