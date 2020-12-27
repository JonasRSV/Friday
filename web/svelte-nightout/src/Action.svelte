<script>
  import {Col, Container, Row} from 'sveltestrap';
  import { IconLookup } from "./action/IconLookup.js";

export let action;
export let onNameClick;
export let onCommandClick;

export function updateName(newName) {
  action.name = newName;
}

let icons = IconLookup.lookup(action.update);
  
</script>


<style>

  .vertical-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .horizontal-center {
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
  }

  .action-height { height: 40px; }
  .keyword { font-size: 22pt; }

  .keyword:hover {
    cursor:pointer;
    opacity: 0.8;
  }

  .vendors:hover {
    cursor: pointer;
    opacity: 0.8;
  }

  .icon { width: 30px; }


</style>


<Container fluid class=container-xs>
  <Row> 
    <Col xs=3 sm=3 md=3 lg=3> </Col>
    <Col xs=4 sm=4 md=4 lg=4 class="text-center"> 
      <div class="keyword vertical-center action-height" on:click={onNameClick}>
        {action.name}
      </div>
    </Col>

    <Col xs=2 sm=2 md=2 lg=2 class="vendors text-left"> 
      <div class="vendors vertical-center action-height">
        <div class="horizontal-center" on:click={onCommandClick}>
          {#each icons as icon}
            <div class="icon">
              <svelte:component this={icon.component} {...icon.props}/>
            </div>
          {/each}
        </div>
      </div>
    </Col>
    <Col xs=5 sm=5 md=5 lg=5> </Col>

  </Row>
</Container>
