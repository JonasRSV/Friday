<script>
  import {Col, Container, Row} from 'sveltestrap';
  import { IconLookup } from "./action/IconLookup.js";
  import BubbleBanner from "./banners/BubbleBanner.svelte"

export let action;
export let openMechanic;
export let onRemoveClick;
export let icons = [];

export function setKeyword(newKeyword) {
  action.keyword = newKeyword;
}

export function setCommand(newCommand) {
  action.command = newCommand;

  // Update icons when we set new command
  icons = IconLookup.lookup(action);
}


let removeClicked = (e) => {
  e.stopPropagation();
  onRemoveClick(action);
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
    justify-content: center;
  }

  .action-height { height: 110px; }
  .keyword { font-size: 22pt; }
  .icon { width: 30px; }


  .remove {
    height: 100%;
    widows: 100%;
    background-color: rgba(120, 20, 20, 0.7);
  }

  .remove:hover {
    opacity: 0.8;
    cursor: pointer;
  }

  .empty-space {
    height: 30px;
  }

  .opacity-hover:hover {
    opacity: 0.8;
    cursor: pointer;
  }

@media screen and (max-width: 500px) {
  .keyword { font-size: 18pt; }
}



</style>


<Container fluid class=container-xs>
    <Row> 
      <Col xs=0 sm=2 md=2 lg=2> </Col>
      <Col xs=12 sm=8 md=8 lg=8>
        <div class="opacity-hover" on:click={() => openMechanic(action)}>
          <Container fluid class=container-xs>
            <BubbleBanner>
              <Row>
                <Col xs=3 sm=3 md=3 lg=3> 
                  <div class="remove" on:click={removeClicked}>
                  </div>
                </Col>
                <Col xs=6 sm=6 md=6 lg=6 class="text-center"> 
                  <div class="keyword vertical-center action-height" >
                    {action.keyword}
                  </div>
                </Col>

                <Col xs=3 sm=3 md=3 lg=3 class="vendors text-left"> 
                  <div class="vendors vertical-center action-height">
                    <div class="horizontal-center">
                      {#each icons as icon}
                        <div class="icon">
                          <svelte:component this={icon.component} {...icon.props}/>
                        </div>
                      {/each}
                    </div>
                  </div>
                </Col>
              </Row>
            </BubbleBanner>
          </Container>
        </div>
      </Col>
      <Col xs=0 sm=2 md=2 lg=2> </Col>
    </Row>

  <div class="empty-space"></div>
</Container>
