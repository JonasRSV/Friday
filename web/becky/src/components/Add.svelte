<script>

export let click;

</script>

<style>

  .add-button {
    position: fixed;
    bottom: 15%;
    right: 5%;

    width: 72px !important;
    height: 72px !important;

    border-radius: 50%;

    background-color: #00ffc2;
    color: #303841;
    overflow: hidden;

    border: none;

    justify-content: center
  }

  .plus {
    font-size: 30pt;
    height: 100%;

  }

</style>



<button class="d-flex add-button shadow text-center flex-row justify-content-center" on:click={click}> 
  <div class="plus d-flex flex-column justify-content-center">+</div>
</button>



