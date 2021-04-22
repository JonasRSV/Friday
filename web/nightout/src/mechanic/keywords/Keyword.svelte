
<script>
import { Row, Col } from 'sveltestrap';
import WaveBanner from "./../../banners/WaveBanner.svelte"
import FaTrash from 'svelte-icons/fa/FaTrash.svelte'
import FaPencilAlt from 'svelte-icons/fa/FaPencilAlt.svelte'
import FaPlay from 'svelte-icons/fa/FaPlay.svelte'

export let id;
export let keyword;
export let selecting;
export let onRemoveClick;
export let onPlayClick;

let renaming = false;

let activateSelection = (e) => {
  selecting = true;
  e.stopPropagation();
}

let activateRenaming = (e) => {
  renaming = true;
  e.stopPropagation();
}

let submitRenaming = (e) => {
  console.log("e", e)
  keyword = e.target.elements.name.value;
  renaming = false;
  selecting = false;
  e.stopPropagation();
}

let localClick = (handler) => (e) => {
  e.stopPropagation();
  handler();
}

</script>


<style>

.activate-selection:hover {
  opacity: 0.9;
  cursor: pointer;

}

.input {
  height: 60px;
  font-size: 22pt;
  background-color: rgba(0, 0, 0, 0.2);
  color: white;

}

.text-background {
  font-size: 16pt;
  display: inline-block;
}

.icon-onclick {
  height: 50px;
}

.icon-onclick:hover {
  opacity: 0.7;
  cursor: pointer;
}

.red {
  color: red;
}

.purple {
  color: pink;
}

.yellow {
  color: yellow;
}

.click-area {
  position: absolute;
  height: 100px;
  width: 100px;
  top: -25px;
  left: 10px;
}

</style>



{#if renaming && selecting}
  <WaveBanner>
    <div class="d-flex flex-row justify-content-center" on:click={localClick(() => null)}>
      <form on:submit={submitRenaming} class="col-10">
        <input id="name" value={keyword} class="col-12 text-center input" type="text" aria-label="Large" aria-describedby="inputGroup-sizing-sm">
      </form>
    </div>
  </WaveBanner>
{:else if selecting}
<WaveBanner>
  <Row> 
    <Col xs=4 sm=4 md=4 lg=4 >
      <div class="icon-onclick red" >
        <div class="click-area" on:click={localClick(() => onRemoveClick())}> </div>
        <FaTrash />
      </div>
    </Col>
    <Col xs=4 sm=4 md=4 lg=4 >
      <div class="icon-onclick yellow" >
        <div class="click-area" on:click={activateRenaming}> </div>
        <FaPencilAlt />
      </div>
    </Col>
    <Col xs=4 sm=4 md=4 lg=4 >
      <div class="icon-onclick purple" >
        <div class="click-area" on:click={localClick(() => onPlayClick())}> </div>
        <FaPlay />
    </div>
    </Col>
  </Row>
</WaveBanner>
{:else if keyword != ""}
<div class="activate-selection" on:click={activateSelection}>
  <WaveBanner active>
    <div class="text-container">
      <div class="text-background">
        {keyword}
      </div>
    </div> 
  </WaveBanner>
</div>
{:else}
<div class="activate-selection" on:click={activateSelection}>
  <WaveBanner>
    <div class="text-container">
      <div class="text-background">
        {id}
      </div>
    </div> 
  </WaveBanner>
</div>
{/if}


