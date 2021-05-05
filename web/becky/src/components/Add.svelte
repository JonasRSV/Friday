<script>

export let click;

</script>

<style>

  .add-button {
    position: fixed;
    bottom: 20%;
    right: 5%;

    width: 72px;
    height: 72px;

    border-radius: 50%;

    background-color: pink;
    color: black;
    font-size: 36pt;

    border: solid 1px purple;

    justify-content: center


  }

</style>



<button class="add-button shadow text-center" on:click={click}> + </button>



