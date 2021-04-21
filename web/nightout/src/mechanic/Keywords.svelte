<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Col, Row } from 'sveltestrap';
import FaRegPlusSquare from 'svelte-icons/fa/FaRegPlusSquare.svelte'
import BubbleBanner from "./../banners/BubbleBanner.svelte"
import GreenBubbleBanner from "./../banners/GreenBubbleBanner.svelte"

// Current active keyword
export let activeKeyword;

// Function to call on-change of active keyword
export let updateKeyword;

export let newKeyword;

// All keywords available
export let keywords = [];

/*let onActiveClick = (e) => e.stopPropagation();*/
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
  height: 80px;
  overflow: hidden;
  display: flex;
  flex-direction: column; 
  justify-content: center;
  font-size: 18pt;
}

.empty-space {
  height: 10px;
}

.top-space {
  height: 50px;
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

.title-text {
  font-size: 22pt;
}

</style>


<Container fluid class="full-height">
  <Row>
    <Col xs=12 sm=12 md=12 lg=12>
    <div class="top-space"></div>
    </Col>
  </Row>
  <Row class="text-center">
    <Col xs=12 sm=12 md=12 lg=12>
      <div class="title-text">When you say...</div>
    </Col>
  </Row>
  <Row>
    <div class="empty-space"></div>
    <div class="empty-space"></div>
    <div class="empty-space"></div>
  </Row>
{#each keywordProperties as keyword }
  <Row>
    <Col xs=1 sm=3 md=3 lg=3></Col>
    <Col xs=10 sm=6 md=6 lg=6>
      {#if keyword.active}
        <div class="opacity-hover">
          <GreenBubbleBanner>
            <div class="full-width" on:click={(e) => onInactiveClick(e, keyword.name)}>
              <div class="keyword active" > {keyword.name} </div>
            </div>
          </GreenBubbleBanner>
        </div>
      {:else}
        <div class="opacity-hover">
          <BubbleBanner>
            <div class="full-width"  on:click={(e) => onInactiveClick(e, keyword.name)}>
              <div class="keyword"> {keyword.name} </div>
            </div>
          </BubbleBanner>
        </div>
      {/if}
    </Col>
    <Col xs=1 sm=3 md=3 lg=3></Col>
  </Row>
  <Row>
    <div class="empty-space"></div>
  </Row>
{/each}

<Row>
  <div class="empty-space"></div>
  <div class="empty-space"></div>
</Row>

<Row class="text-center"> 
  <div class="horizontal-center">
    <div class="add-icon" on:click={onNewClick}>
      <FaRegPlusSquare/> 
    </div>
  </div>
</Row>

</Container>
