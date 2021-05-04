<script>
import { onMount } from "svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

// self reference
export let root;
export let keyword;


// 
export let setComponent;


onMount (async () => { 


});



</script>

<style>


</style>



<p> Keywords <span> <button> edit </button> </span></p> 
<hr>
<div class="d-flex">
  <div class="col-12">
    {keyword}
  </div>
</div>

