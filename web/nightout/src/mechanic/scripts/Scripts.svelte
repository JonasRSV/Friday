<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row, Col } from 'sveltestrap';
import { FridayAPI } from "../../FridayAPI.js";
import { Spinner } from 'sveltestrap';
import { onMount } from "svelte";
import WaveBanner from "./../../banners/WaveBanner.svelte"
import FaSync from 'svelte-icons/fa/FaSync.svelte'
import Script from "./Script.svelte"

export let command;
export let sync;
export let deactivate;

let is_syncing = false;
let renderScripts = false;
let scripts = [];


let toggle = (script) => {
  if (script.active) {
    command.scripts = command.scripts.filter(elem => elem != script.name);
    script.active = false;
  } else {
    command.scripts.push(script.name);
    script.active = true;
  }

  // updates UI
  command.setScripts(command.scripts);

  // Forces re-render
  scripts = scripts;
}

async function onSyncClick(e) {
  e.stopPropagation();
  is_syncing = true;

  sync();
  await (new Promise(resolve => setTimeout(resolve, 1000)));
  is_syncing = false;
  deactivate();
}


onMount (async () => { 
  let allScripts = await FridayAPI.getAllScripts();

  allScripts.forEach(script => {
    scripts.push(
      {
        "name": script,
        "active": command.scripts.includes(script)
      }
    );
  });

  renderScripts = true;
});

</script>


<style>

.script {
  position: relative;
  width: 350px;
  padding-right: 15px;
  padding-left: 15px;
}

.opt-icon {
  height: 60px;
}

.opt-icon:hover {
  opacity: 0.9;
  cursor: pointer;
}

.opt-container {
  height: 100px;
  width: 120px;
  margin-left: 15px;
  margin-right: 15px;
}

.bottom-options {
  position: fixed;
  bottom: 0px;
  width: 100%;
  height: 150px;
  background-color: rgba(47, 54, 64,0.97);
  padding-top: 20px;

}

.margin-top-bottom {
  margin-top: 200px;
  margin-bottom: 200px;
}
</style>



<div class="event-capture" on:click={(e) => e.stopPropagation()}>

{#if is_syncing}
<div class="middle-screen">
  <h1>Syncing with Friday...</h1>
  <Spinner info type="grow" />
</div>
{:else if renderScripts}
<Container fluid  >
    <div class="d-flex flex-wrap flex-row justify-content-center margin-top-bottom">
        {#each scripts as script (script.name)}
          <div class="script my-3">
            <Script name={script.name} 
                    active={script.active}
                    onClick={() => toggle(script)}/>
          </div>
          {/each}
    </div>
  </Container>

<div class="bottom-options d-flex flex-row justify-content-center">
    <div class="opt-container" on:click={onSyncClick}>
      <WaveBanner>
        <div class="opt-icon">
          <FaSync/>
        </div>
      </WaveBanner>
    </div>
</div>

{:else}
  <div class="middle-screen">
    <h1>Fetching Scripts..</h1>
    <Spinner info type="grow" />
  </div>
{/if}
</div>
