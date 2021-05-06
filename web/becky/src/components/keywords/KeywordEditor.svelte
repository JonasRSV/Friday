<script>
import { onMount } from "svelte";
import ClipBar from "./clips/ClipBar.svelte";
import ClipOptions from "./clips/ClipOptions.svelte";
import RecordingOption from "./recording/RecordingOption.svelte"
import RecordingTransition from "./recording/RecordingTransition.svelte";
import RemovingTransition from "./recording/RemovingTransition.svelte";
/*import { FridayAPI } from "./FridayAPI.js"*/

export let setComponent;
export let root;

export let keyword;
export let clips;

export let goBack;
export let syncFriday;

// newest recorded clip
export let newestClip = null;
// if true we're in the recording flow
export let recordingFlow = false;


// show options of this clip
// don't show if null
let showingClip = null;

onMount (async () => { 
});

let onRecordingFlowAccept = () => {
  recordingFlow = false;
}

let onRecordingFlowRetry = (clip) => {
  clips = clips.filter((item) => item != clip);

  // Recording will sync with friday which removes any dangling clips
  onRecordingClick();
}

let removeClip = (clip) => {
  setComponent(
    RemovingTransition, {
     "clip": clip,
     "onSync": () => {
       clips = clips.filter((item) => item != clip); 
       return syncFriday(keyword, clips);
     },
     "onSuccess": () => {
        // go back to this component
        setComponent(root, {
          "root": root,
          "setComponent": setComponent,
          "keyword": keyword,
          "clips": clips,
          "goBack": goBack,
          "syncFriday": syncFriday,
          "newestClip": null,
          "recordingFlow": false
        });

     },
     "onFailure": () => {
        console.log("failed removing recording")

        // go back to this component
        setComponent(root, {
          "root": root,
          "setComponent": setComponent,
          "keyword": keyword,
          "clips": clips,
          "goBack": goBack,
          "syncFriday": syncFriday,
          "newestClip": null,
          "recordingFlow": false
        });
      }
    }
  );
}

let playClip = (clip) => {
  console.log("Playing", clip);
}

let onClipClick = (clip) => showingClip = clip;
let onRecordingClick = () => {
  setComponent(
    RecordingTransition, {
     "onSync": (clip) => {
        clips.push(clip);
        return syncFriday(keyword, clips);
     },
     "onSuccess": (recording) => {
        // go back to this component
        setComponent(root, {
          "root": root,
          "setComponent": setComponent,
          "keyword": keyword,
          "clips": clips,
          "goBack": goBack,
          "syncFriday": syncFriday,
          "newestClip": recording,
          "recordingFlow": true
        });

     },
     "onFailure": () => {
        // go back to this component
        setComponent(root, {
          "root": root,
          "setComponent": setComponent,
          "keyword": keyword,
          "clips": clips,
          "goBack": goBack,
          "syncFriday": syncFriday,
          "newestClip": null,
          "recordingFlow": false
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
  z-index: 10;
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
    <ClipOptions bind:clip={showingClip} remove={removeClip} play={playClip}/>
  {/if}

  {#if recordingFlow}
    <RecordingOption 
                 clip={newestClip} 
                 accept={onRecordingFlowAccept} 
                 retry={onRecordingFlowRetry}
                 remove={(clip) => {
                   removeClip(clip);
                   newestClip = null;
                   recordingFlow = false;
                 }}
                 play={playClip}/>
  {/if}

  <div class="fixed-bottom d-flex flex-row">
    <button class="recording button col-12" on:click={onRecordingClick}> </button>
  </div>

</main> 









