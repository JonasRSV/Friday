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

  background-color: #3a4750;
  color: #eeeeee;
  border: none;

  -webkit-box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15); 
  box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.15);

}

.vertical {
  height: 100%;
}

</style>

<div class="bar mb-3 shadow rounded text-center d-flex justify-content-center">
  <div class="vertical d-flex flex-column justify-content-center">
    <h2 class="script-container">
      {script}
    </h2>
  </div>
</div>





