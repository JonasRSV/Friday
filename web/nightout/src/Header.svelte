<script>
  import {Col, Container, Row} from 'sveltestrap';

  export let title;
</script>


<style>

  .header-title {
    font-size: 40pt;
  }

  .header-container {
    height: 140px;
  }

</style>


<Container fluid class="container-xs ">
  <div class="header-container">
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12 class="text-center"> 
        <h1 class="header-title"> {title} </h1>
      </Col>
    </Row>
  </div>
</Container>
