<script>
  import GiMineExplosion from 'svelte-icons/gi/GiMineExplosion.svelte'
  import {Col, Container, Row} from 'sveltestrap';
  import { IconLookup } from "./action/IconLookup.js";

export let action;
export let onNameClick;
export let onCommandClick;
export let onRemoveClick;
export let icons = [];

export function setName(newName) {
  action.name = newName;
}

export function setCommand(newCommand) {
  action.command = newCommand;

  // Update icons when we set new command
  icons = IconLookup.lookup(action);
}


icons = IconLookup.lookup(action);
  
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


  .remove {
    display: flex;
    flex-direction: row;
    justify-content: center;

  }

  .remove-icon {
    color: red;
    width: 30px;
    height: 30px;
  }

  .remove-icon:hover {
    cursor: pointer;
    opacity: 0.8;
  }

  .empty-space {
    height: 80px;
  }

@media screen and (max-width: 500px) {
  .keyword { font-size: 18pt; }
}



</style>


<Container fluid class=container-xs>
  <Row> 
    <Col xs=0 sm=2 md=2 lg=2> </Col>
    <Col xs=2 sm=1 md=1 lg=1> 
      <div class="remove">
        <div class="remove-icon" on:click={() => onRemoveClick(action)}>
          <GiMineExplosion/>
        </div>
      </div>
    </Col>
    <Col xs=6 sm=4 md=4 lg=4 class="text-center"> 
      <div class="keyword vertical-center action-height" on:click={() => onNameClick(action)}>
        {action.name}
      </div>
    </Col>

    <Col xs=4 sm=2 md=2 lg=2 class="vendors text-left"> 
      <div class="vendors vertical-center action-height">
        <div class="horizontal-center" on:click={() => onCommandClick(action)}>
          {#each icons as icon}
            <div class="icon">
              <svelte:component this={icon.component} {...icon.props}/>
            </div>
          {/each}
        </div>
      </div>
    </Col>
    <Col xs=0 sm=5 md=5 lg=5> </Col>
    <Col xs=0 sm=0 md=0 lg=0> </Col>
  </Row>

  <div class="empty-space"></div>
</Container>
