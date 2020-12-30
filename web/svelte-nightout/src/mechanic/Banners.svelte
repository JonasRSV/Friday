
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import { Container, Row } from 'sveltestrap';
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

  .empty-space {
    height: 20px;
  }

</style>


<Container fluid class="container-keywords">
  <Row> 
    <div class='banner on-click' on:click={(e) => onBannerClickLocal(e, HueControl)} > 
      <HueBanner /> 
    </div> 
  </Row>
  <div class="empty-space"></div>
  <Row> 
    <div class='banner inactive' on:click={(e) => e.stopPropagation()} > 
      <ScriptBanner /> 
    </div> 
  </Row>

  <div class="empty-space"></div>

  <Row> 
    <div class='banner inactive' on:click={(e) => e.stopPropagation()} > 
      <SpotifyBanner /> 
    </div> 
  </Row>


  <div class="empty-space"></div>
</Container>

