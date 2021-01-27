
<script>
import { Container, Row, Col } from 'sveltestrap';
import WaveBanner from "./../../banners/WaveBanner.svelte"
import GreenWaveBanner from "./../../banners/GreenWaveBanner.svelte"
import FaTrash from 'svelte-icons/fa/FaTrash.svelte'
import FaPencilAlt from 'svelte-icons/fa/FaPencilAlt.svelte'
import FaPlay from 'svelte-icons/fa/FaPlay.svelte'
import FaPlus from 'svelte-icons/fa/FaPlus.svelte'

export let id;
export let selecting;
export let selected;
export let onRemoveClick;
export let onSelectClick;
export let onPlayClick;
export let onRename;


let activateSelection = (e) => {
  selecting = true;
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

.id-text {
  font-size: 16pt;
}

.icon-onclick {
  height: 50px;
}

.icon-onclick:hover {
  opacity: 0.7;
  cursor: pointer;
}

.green {
  color: rgb(20, 255, 20);
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

</style>



{#if selecting}
<WaveBanner>
  <Row> 
    <Col xs=3 sm=3 md=3 lg=3 >
      <div class="icon-onclick red" on:click={localClick(() => onRemoveClick())}>
        <FaTrash />
      </div>
    </Col>
    <Col xs=3 sm=3 md=3 lg=3 >
      <div class="icon-onclick yellow" on:click={localClick(() => console.log("renaming"))}>
        <FaPencilAlt />
      </div>
    </Col>
    <Col xs=3 sm=3 md=3 lg=3 >
      <div class="icon-onclick purple" on:click={localClick(() => onPlayClick())}>
        <FaPlay />
      </div>
    </Col>
    <Col xs=3 sm=3 md=3 lg=3 >
    {#if selected}
      <div class="icon-onclick red" on:click={localClick(() => onSelectClick())}>
        <FaPlus />
      </div>
    {:else}
      <div class="icon-onclick green" on:click={localClick(() => onSelectClick())}>
        <FaPlus />
      </div>
    {/if}
    </Col>
  </Row>
</WaveBanner>
{:else}
<div class="activate-selection" on:click={activateSelection}>
  {#if selected}
    <GreenWaveBanner>
      <div class="id-text">{id}</div> 
    </GreenWaveBanner>
  {:else}
    <WaveBanner>
      <div class="id-text">{id}</div> 
    </WaveBanner>
  {/if}
</div>
{/if}


