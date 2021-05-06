<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let click;
export let clip;



onMount (async () => { 


});



</script>

<style>

.bar {
  height: 70px;
  width: 100%;
  background-color: white;
}

.bar:hover {
  opacity: 0.8;
  cursor: pointer;
}


.vertical {
  height: 100%;
}



</style>

<button class="bar mb-3 shadow rounded text-center d-flex justify-content-center" on:click={click}>
  <div class="vertical d-flex flex-column justify-content-center font-weight-light">
    {clip}
  </div>
</button>





