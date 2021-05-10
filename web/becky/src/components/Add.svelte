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
    position: absolute;
    margin: 0 auto;
    top: 28px;
    left: 36px;

    /*To truly get it into the center*/
    transform: translate(-50%, -50%);

    font-size: 40pt;

  }

</style>



<button class="d-flex add-button shadow text-center flex-row justify-content-center" on:click={click}> 
  <div class="plus d-flex flex-column justify-content-center">+</div>
</button>



