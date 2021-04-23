<script>
  import {Col, Container, Row} from 'sveltestrap';
  import BubbleBanner from "./banners/BubbleBanner.svelte"
  import GiSplitCross from 'svelte-icons/gi/GiSplitCross.svelte'

export let command;
export let openMechanic;
export let onRemoveClick;

export function setKeyword(newKeyword) {
  command.keyword = newKeyword;
}

export function setScripts(newScripts) {
  command.scripts = newScripts;

}


let removeClicked = (e) => {
  e.stopPropagation();
  onRemoveClick(command);
}

  
</script>


<style>

  .vertical-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .command-height { height: 110px; }
  .keyword { font-size: 3vw; }


  .remove {
    width: 100%;
    height: 110px;

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

@media screen and (max-width: 1110px) {
  .keyword { font-size: 6vw; }
}

@media screen and (max-width: 500px) {
  .keyword { font-size: 8vw; }
}



</style>


<Container fluid class=container-xs>
    <Row> 
      <Col xs=0 sm=2 md=2 lg=2> </Col>
      <Col xs=12 sm=8 md=8 lg=8>
        <div class="opacity-hover" on:click={() => openMechanic(command)}>
          <Container fluid class=container-xs>
            <BubbleBanner>
              <Row>
                <Col xs=4 sm=4 md=4 lg=4> 
                  <div class="d-flex flex-column justify-content-center remove" on:click={removeClicked}>
                    <GiSplitCross />
                  </div>
                </Col>
                <Col xs=8 sm=8 md=8 lg=8 class="text-center"> 
                  <div class="keyword vertical-center command-height" >
                    {command.keyword}
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
