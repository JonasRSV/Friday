<script>
import WaveBanner from "./../../banners/WaveBanner.svelte"

export let name;
export let active;

export let onClick;


let localClick = (handler) => (e) => {
  e.stopPropagation();
  handler();
}

</script>


<style>

.activate-selection:hover {
  opacity: 0.9;
  cursor: pointer;
}


</style>



{#if active}
<div class="activate-selection" on:click={localClick(onClick)}>
  <WaveBanner active>
    <div class="text-container">
      <div class="text-background">
        {name}
      </div>
    </div> 
  </WaveBanner>
</div>
{:else}
<div class="activate-selection" on:click={localClick(onClick)}>
  <WaveBanner>
    <div class="text-container">
      <div class="text-background">
        {name}
      </div>
    </div> 
  </WaveBanner>
</div>
{/if}


