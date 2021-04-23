<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row, Col } from 'sveltestrap';
import { FridayAPI } from "../../FridayAPI.js";
import { Spinner } from 'sveltestrap';
import { onMount } from "svelte";
import Script from "./Script.svelte"

export let command;
export let sync;

let renderScripts = false;
let scripts = [];

let update_friday = true;

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

  if (update_friday) {
    update_friday = false;

    // update in two seconds, to prevent spamming API
    setTimeout(() => {
      sync()

      // can now update again
      update_friday = true;
    }, 2000);
  }
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

.top-separator {
   height: 100px;
}

.script {
  position: relative;
  width: 350px;
  padding-right: 15px;
  padding-left: 15px;
}
</style>



{#if renderScripts}
<Container fluid>
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="top-separator"></div>
      </Col>
    </Row>
  <Row class="text-center">
    <Col xs=12 sm=12 md=12 lg=12>
      <h1>Run...</h1>
    </Col>
  </Row>
    <div class="d-flex flex-wrap flex-row justify-content-center">
        {#each scripts as script (script.name)}
          <div class="script my-3">
            <Script name={script.name} 
                    active={script.active}
                    onClick={() => toggle(script)}/>
          </div>
          {/each}
    </div>
  </Container>

{:else}
  <div class="middle-screen">
    <h1>Fetching Scripts..</h1>
    <Spinner info type="grow" />
  </div>
{/if}
