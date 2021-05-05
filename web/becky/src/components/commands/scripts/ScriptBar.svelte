<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let script;



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




</style>

<div class="bar mb-3 shadow rounded text-center d-flex justify-content-center">
  <div class="d-flex flex-column justify-content-center font-weight-light">
    {script}
  </div>
</div>





