
<script>
import { Row, Col } from 'sveltestrap';
import NameInputBanner from "./NameInputBanner.svelte"
import { onMount } from "svelte";

export let name;
export let onComplete;

let bannerClick = (e) => {
  e.stopPropagation();
}

let inputElem = null; 

let keyClicked = (e) => {
  name = inputElem.value;

  if (e.key == "Enter") {
    onComplete();
  }
}

onMount (() => { 
  inputElem = document.getElementById("name-input");
});

</script>


<style>
  .title {
    font-size: 18pt;
    text-align: center;
  }

</style>



<div class="inputBanner" on:click={bannerClick}>
<NameInputBanner>
  <Row class="text-center"> 
    <Col xs=12 sm=12 md=12 lg=12>
      <div class="title">
        Keyword 
      </div>
    </Col>
  </Row>
  <Row>
    <Col xs=12 sm=12 md=12 lg=12>
      <input id="name-input" lass="name-input" type="text" on:keyup={keyClicked}> 
    </Col>
  </Row>
</NameInputBanner>
</div>


