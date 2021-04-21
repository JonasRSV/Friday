<script>
  import FaRegLightbulb from 'svelte-icons/fa/FaRegLightbulb.svelte';

  export let on;
  
</script>


<style>
.vertical-center {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.lamp-on {
  color: yellow;
}

.lamp-off {
  color: purple;
}

</style>


{#if on}
<div class="lamp-on vertical-center">
  <FaRegLightbulb />
</div>
{:else}
<div class="lamp-off vertical-center">
  <FaRegLightbulb />
</div>
{/if}

