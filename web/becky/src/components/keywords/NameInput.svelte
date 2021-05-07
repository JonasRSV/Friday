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
let input = "Name here";

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
    padding-bottom: 25px;
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 25px;
    color: white;
    width: 90%;
    right: 10%;
    left: 10%;

    background-color: #3a4750;
  }

  .middle-screen {
    width: 100%;
    position: fixed;
    margin: 0 auto;
    top: 50%;
    left: 50%;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);

  }

  .button {
    height: 60px;
    border: none;
  }

  .input {
    display: block;
    width: 80%;
    height: 60px;
    font-size: 22pt;
    text-align: center;

    border: none;

    background-color: #eeeeee;
    font-family: Cambria;
    font-size: 16px;
    border-radius: 10px;
  }

  .input-container {
    width: 100%;
  }
  
  .unacceptable {
    border-color: red;
  }

  .button-container {
    padding-left: 15%;
    padding-right: 15%;
      
  }

  .button-add {
    background: url("/assets/icons/keyword-name-ok.svg") no-repeat;
    background-color: #ff6f00;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 5px;
    border-radius: 10px;
  }

  .button-cancel {
    border: solid 3px #ff6f00;
    background-color: rgba(0, 0, 0, 0);
    background: url("/assets/icons/keyword-name-cancel.svg") no-repeat;
    background-position: center;
    background-size: contain;
    background-repeat: no-repeat;
    background-origin: content-box;
    padding: 5px;
    border-radius: 10px;

  }


</style>

<div class="layover" in:fly="{{ y: 800, duration: 500 }}" out:fly="{{y: 800, duration: 500}}">
  <div class="middle-screen rounded d-flex justify-content-center">
    <div class="options rounded">
      <div class="input-container d-flex flex-row justify-content-center">
        {#if acceptable}
          <input class="mb-5 input" type="text" id="keyword" bind:value={input} on:input={inputValidator} use:focus autocomplete="off">
        {:else}
          <input class="mb-5 input unacceptable" type="text" id="keyword" bind:value={input} on:input={inputValidator} use:focus autocomplete="off">
        {/if}
      </div>
      <div class="button-container d-flex flex-row">
        <button class="button button-cancel col-5" on:click={cancel}></button>
        <div class="col-2"> </div>
        <button class="button button-add col-5" on:click={add}></button>
      </div>
    </div>
  </div>
</div>





