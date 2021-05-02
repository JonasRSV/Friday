
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row, Col } from 'sveltestrap';
import ScriptBanner from './scripts/ScriptBanner.svelte';
import Scripts from './scripts/Scripts.svelte';


export let onBannerClick;

let onBannerClickLocal = (e, component) => {
  e.stopPropagation();
  onBannerClick(component);
}

</script>


<style>

  .banner {
    width: 100%;
  }

  .on-click:hover {
    cursor: pointer;
    opacity: 0.8;
  }

</style>


<Container fluid class="container-keywords">
  <Row> 
    <Col xs=1 sm=2 md=2 lg=2></Col>
    <Col xs=10 sm=8 md=8 lg=8>
    <div class='banner on-click' on:click={(e) => onBannerClickLocal(e, Scripts)} > 
      <ScriptBanner /> 
    </div> 
    </Col>
    <Col xs=1 sm=2 md=2 lg=2></Col>
  </Row>


</Container>

