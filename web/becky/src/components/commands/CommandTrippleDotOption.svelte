<script>
import { onMount } from "svelte";
import { fly } from 'svelte/transition';
/*import { FridayAPI } from "./FridayAPI.js"*/

export let name;
export let remove;
export let goBack;


onMount (async () => { 


});



</script>

<style>
  .layover {
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    height: 100%;
    width: 100%;
    z-index: 9999;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);
  }


  .options {
    padding-bottom: 25px;
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 25px;
    color: white;
    width: 90%;
    right: 10%;
    left: 10%;

    border-radius: 10px;

    background-color: #3a4750;
  }

  .middle-screen {
    width: 80%;
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }

  .remove-button {
    height: 60px;
    border-radius: 10px;
    border: none;

    background: url("/assets/icons/trashcan-grey.svg");
    background-color: #ff6f00;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 15px; 
    z-index: 10;
  }


  .goback-button {
    height: 60px;
    border-radius: 10px;
    border: none;

    background: url("/assets/icons/keyword-name-cancel.svg");
    border: solid 3px #ff6f00;
    background-color: #3a4750;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 10px; 
    z-index: 10;
  }

</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{ y: 800, duration: 500 }}">
  <div class="middle-screen d-flex flex-row justify-content-center">
    <div class="options">
        <header class="mb-5 mt-3">
          <h3 class="text-center">
            {name}
          </h3>
        </header>

        <div class="d-flex flex-row justify-content-center mb-4">
          <button class="remove-button col-6" on:click={() => remove()}> </button>
        </div>
        <div class="d-flex flex-row justify-content-center mb-2">
          <button class="goback-button col-6" on:click={goBack}> </button>
        </div>
    </div>
  </div>
</div>





