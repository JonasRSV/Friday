<script>
import { onMount } from "svelte";
import { fly } from 'svelte/transition';
/*import { FridayAPI } from "./FridayAPI.js"*/


export let keywords;
export let addKeyword;
export let cancel;


onMount (async () => { 


});

// name in input field
let input = "...";

// if input is acceptable
let acceptable = true;


// add keyword
let add = () => {
  if (acceptable) {
    addKeyword(input);
  }
}

let focus = (el) => el.focus();

// validate input
let inputValidator = () => acceptable = ! (input in keywords);

</script>

<style>
  .layover {
    top: 0;
    left: 0;
    right: 0;
    position: fixed;
    height: 100%;
    width: 100%;

    background-color: rgba(0.0, 0.0, 0.0, 0.8);

    z-index: 9999;
  }


  .options {
    color: white;
    width: 100%;
    right: 0;
    left: 0;
  }

  .middle-screen {
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);
  }

  .button {
    height: 80px;
  }

  .input {
    width: 80%;
    height: 60px;
    font-size: 22pt;
  }
  
  .unacceptable {
    border-color: red;
  }


</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{y: 800, duration: 500}}">
  <div class="middle-screen options">
    {#if acceptable}
      <input class="mb-5 input" type="text" id="keyword" bind:value={input} on:input={inputValidator} use:focus autocomplete="off">
    {:else}
      <input class="mb-5 input unacceptable" type="text" id="keyword" bind:value={input} on:input={inputValidator} use:focus autocomplete="off">
    {/if}
    <div class="d-flex flex-row">
      <button class="button col-6" on:click={cancel}> - </button>
      <button class="button col-6" on:click={add}> + </button>
    </div>
  </div>
</div>





