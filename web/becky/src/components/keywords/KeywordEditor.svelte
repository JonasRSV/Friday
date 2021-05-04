<script>
import { onMount } from "svelte";
import ClipBar from "./clips/ClipBar.svelte";
import ClipOptions from "./clips/ClipOptions.svelte";
import RecordingTransition from "./recording/RecordingTransition.svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let root;

export let keyword;

export let setComponent;
export let goBack;

let clips = []


// show options of this clip
// don't show if null
let showingClip = null;

onMount (async () => { 
  clips = [
    "123-222-333-111.wav",
    "223-222-333-111.wav",
    "223-333-333-111.wav",
  ]

});


let onClipClick = (clip) => showingClip = clip;

let onRecordingClick = () => {
  let recordingPromise = new Promise((resolve, _) => {
    setTimeout(() => {
      resolve("123-222-333-333.wav");
    }, 3000);
  });

  setComponent(
    RecordingTransition, {
     "recordingPromise": recordingPromise,
      "onSuccess": (recording) => {
        console.log("successfully recorded", recording)

        // go back to this component
        setComponent(root, {
          "keyword": keyword,
          "goBack": goBack
        });

      },
      "onFailure": () => {
        console.log("failed recording")

        // go back to this component
        setComponent(root, {
          "keyword": keyword,
          "goBack": goBack
        });
      }
    }
  );

}


</script>

<style>

.recording {
  background: url("/assets/icons/recording-icon.svg");
  background-color: white;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-origin: content-box;
  padding: 5px;
}

.button {
  height: 80px;
}

main {
  text-align: center;
  padding: 1em;
  margin: 0 auto;
}
</style>




<main>
  <header class="mb-5">
    <h1>
      {keyword}
    </h1>
  </header>


  {#each clips as clip (clip)}
    <ClipBar bind:clip={clip} click={() => onClipClick(clip)}/>
  {/each}

  <button on:click={goBack}>done</button>

  {#if showingClip != null}
    <ClipOptions bind:clip={showingClip}/>
  {/if}

  <div class="fixed-bottom d-flex flex-row">
    <button class="recording button col-12" on:click={onRecordingClick}> </button>
  </div>
</main> 









