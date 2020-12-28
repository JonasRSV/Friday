<script>
  import GiNewBorn from 'svelte-icons/gi/GiNewBorn.svelte'
  import {Col, Container, Row} from 'sveltestrap';



export let active;
export let onAddClick;

</script>


<style>
  .horizontal-center {
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
  }

  .icon {
    width: 60px;
    height: 60px;
    color: green;
  }

  .icon:hover {
    cursor: pointer;
    opacity: 0.8;
  }
</style>


{#if active}
<Container fluid class=container-xs>
  <Row> 
    <Col xs=12 sm=12 md=12 lg=12 class="text-center"> 
      <div class="horizontal-center">
        <div class="icon" on:click={onAddClick}>
          <GiNewBorn/>
        </div>
      </div>
    </Col>
  </Row>
</Container>
{/if}
