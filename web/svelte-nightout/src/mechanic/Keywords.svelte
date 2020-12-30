<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row, Card } from 'sveltestrap';
import FaPlus from 'svelte-icons/fa/FaPlus.svelte'

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
        "props": {
          "class": "card-header keyword"
        }
      }
  })
}


</script>


<style>

.full-width {
  width: 100%;
}

.on-click:hover {
  cursor: pointer;
  opacity: 0.9;
}

.keyword {
  width: 100%;
  overflow: hidden;
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
  width: 30px;
  height: 30px;
  color: green;
}

.add-icon:hover {
  cursor: not-allowed;
}

</style>


<Container fluid class="container-keywords">
{#each keywordProperties as keyword }
  <Row class="text-center"> 
    {#if keyword.active}
        <div class="full-width" on:click={onActiveClick}>
          <Card color="primary">
          <div class="keyword" {...keyword.props}> {keyword.name} </div>
          </Card>
        </div>
    {:else}
        <div class="on-click full-width"  on:click={(e) => onInactiveClick(e, keyword.name)}>
          <Card color="dark">
          <div  {...keyword.props}> {keyword.name} </div>
          </Card>
        </div>
    {/if}
  </Row>

  <div class="empty-space"></div>
{/each}

<div class="empty-space"></div>
<div class="empty-space"></div>

<Row class="text-center"> 
  <div class="horizontal-center">
    <div class="add-icon" on:click={onNewClick}>
      <FaPlus/> 
    </div>
  </div>
</Row>

</Container>
