
<script>
import { Container, Row, Col } from 'sveltestrap';
import RecordingBanner from "./RecordingBanner.svelte"
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
<RecordingBanner>
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
</RecordingBanner>
{:else}
<div class="activate-selection" on:click={activateSelection}>
<RecordingBanner>
  {#if selected}
    <div class="id-text green">{id}</div> 
  {:else}
    <div class="id-text">{id}</div> 
  {/if}
</RecordingBanner>
</div>
{/if}


