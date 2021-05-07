<script>
  import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let click;
export let keyword;



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

  .bar:hover {
    opacity: 0.8;
    cursor: pointer;
  }

  .vertical {
    height: 100%;
  }



</style>

<button class="bar mb-3 rounded text-center d-flex flex-row justify-content-center" on:click={click}>
  <div class="vertical d-flex flex-column justify-content-center">
    <h2>
      {keyword}
    </h2>
  </div>
</button>





