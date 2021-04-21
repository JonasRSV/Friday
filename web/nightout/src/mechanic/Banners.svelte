
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row, Col } from 'sveltestrap';
import HueBanner from './hue/HueBanner.svelte';
import HueControl from './hue/HueControl.svelte';
import ScriptBanner from './scripts/ScriptBanner.svelte';
import SpotifyBanner from './spotify/SpotifyBanner.svelte';


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

  .inactive:hover {
    cursor: not-allowed;
  }

  .title-text {
    font-size: 22pt;
  }

  .empty-space {
    height: 20px;
  }

</style>


<Container fluid class="container-keywords">
  <Row class="text-center">
    <Col xs=12 sm=12 md=12 lg=12>
      <div class="title-text">I will...</div>
    </Col>
  </Row>
  <div class="empty-space"></div>
  <Row> 
    <Col xs=1 sm=2 md=2 lg=2></Col>
    <Col xs=10 sm=8 md=8 lg=8>
      <div class='banner on-click' on:click={(e) => onBannerClickLocal(e, HueControl)} > 
        <HueBanner /> 
      </div> 
    </Col>
    <Col xs=1 sm=2 md=2 lg=2></Col>
  </Row>
  <div class="empty-space"></div>
  <Row> 
    <Col xs=1 sm=2 md=2 lg=2></Col>
    <Col xs=10 sm=8 md=8 lg=8>
    <div class='banner inactive' on:click={(e) => e.stopPropagation()} > 
      <ScriptBanner /> 
    </div> 
    </Col>
    <Col xs=1 sm=2 md=2 lg=2></Col>
  </Row>

  <div class="empty-space"></div>

  <Row> 
    <Col xs=1 sm=2 md=2 lg=2></Col>
    <Col xs=10 sm=8 md=8 lg=8>
    <div class='banner inactive' on:click={(e) => e.stopPropagation()} > 
      <SpotifyBanner /> 
    </div> 
    </Col>
    <Col xs=1 sm=2 md=2 lg=2></Col>
  </Row>


  <div class="empty-space"></div>
</Container>

