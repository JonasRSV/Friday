<script>

export let click;

</script>

<style>

  .add-button {
    display: inline-block;
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

    font-size: 30pt;

    text-align: center;
    vertical-align: middle;
    line-height: 72px;

  }

  .add-button:before {
    content: "\FF0B";
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
  }



</style>



<button class="add-button shadow text-center" on:click={click}></button>



