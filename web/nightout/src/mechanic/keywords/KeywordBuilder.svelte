
<script>
import { Spinner } from 'sveltestrap';
import { Container, Row, Col } from 'sveltestrap';
import Keyword from './Keyword.svelte';
import WaveBanner from "./../../banners/WaveBanner.svelte"
import IoMdMicrophone from 'svelte-icons/io/IoMdMicrophone.svelte'
import FaSync from 'svelte-icons/fa/FaSync.svelte'
import { FridayAPI } from "./../../FridayAPI.js"
import { playAudio, extractAudioBlob } from "./../../core/Audio";
import { onMount } from "svelte";

export let deactivate;


let recordings = []
let is_syncing = false;
let is_recording = false;

let audio_cache = {}

let onRemoveClick = (state) => {
  state.selecting = false;

  recordings = recordings.filter(v => v.id != state.id);

  // Remove recording on device
  FridayAPI.recordingRemove(state.id);

  recordings = recordings;
}

let onPlayClick = (state) => {
  state.selecting = false;

  if (audio_cache.hasOwnProperty(state.id)) {
      playAudio(audio_cache[state.id]);
  } else {
    FridayAPI.recordingAudio(state.id).then(audio_stream => {
      extractAudioBlob(audio_stream).then(url => {
        audio_cache[state.id] = url;
        playAudio(url);
      });
    });
  }



  recordings = recordings;
}

let onRecordClick = (e) => {
  e.stopPropagation();

  is_recording = true;
  // Rename recording on device
  FridayAPI.recordingNew().then(recording => {
    recordings.push({
      "id": recording.id,
      "keyword": "",
      "selecting": false,
      "is_new": true,
    });

    is_recording = false;
    recordings = recordings;
  });
}

let onSyncClick = (e) => {
    is_syncing = true;
    syncWithFriday();
    e.stopPropagation()
}

let captureEvent = (e) => {
  // If we are selecting something, just de-select
  if (recordings.some(v => v.selecting)) {
    recordings = recordings.map(v => {
      v.selecting = false;

      return v;
    })
  } 
  e.stopPropagation()
}

async function syncWithFriday()  {
  let examples = {}
  recordings.forEach(recording => {
    if (recording.keyword != "") {
      examples[recording.id] = recording.keyword;
    }
  });

  FridayAPI.setExamples(examples);
  await (new Promise(resolve => setTimeout(resolve, 1000)));
  is_syncing = false;
  deactivate();
}

onMount (async () => { 
  FridayAPI.recordingClips().then(clips => {
    FridayAPI.getExamples().then(examples => {
      recordings = clips.ids.map(cid => {
        if (examples.hasOwnProperty(cid)) {
          return {
            "id": cid,
            "keyword": examples[cid],
            "selecting": false,
            "is_new": false,
          }
        } else {
          return {
            "id": cid,
            "keyword": "",
            "selecting": false,
            "is_new": false,
          }
        }
      });
    });
  });
});

</script>


<style>


.keyword-builder-keypress-capture {
  position: fixed;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.0);
  top: 0px;
  left: 0px;

  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  overflow: scroll;
}

.opt-icon {
  height: 60px;
}

.opt-icon:hover {
  opacity: 0.9;
  cursor: pointer;
}

.opt-container {
  height: 100px;
  width: 120px;
  margin-left: 15px;
  margin-right: 15px;
}

.middle-screen {
  position: fixed;
  margin: 0 auto;
  top: 50%;
  left: 50%;

  /*To truly get it into the center*/
  transform: translate(-50%, -50%);
}



.recording {
  position: relative;
  width: 350px;
  padding-right: 15px;
  padding-left: 15px;
}

.bottom-options {
  position: fixed;
  bottom: 0px;
  width: 100%;
  height: 150px;
  background-color: rgba(47, 54, 64,0.97);
  padding-top: 20px;

}

.margin-top-bottom {
  margin-top: 100px;
  margin-bottom: 200px;
}

</style>


<div class="keyword-builder-keypress-capture" on:click={captureEvent}>
{#if is_syncing}
<div class="middle-screen">
  <h1>Syncing with Friday...</h1>
  <Spinner info type="grow" />
</div>
{:else if is_recording}
<div class="middle-screen">
  <h1>Probably Recording...</h1>
  <Spinner info type="grow" />
</div>
{:else}
  <Container fluid>
    <div class="d-flex flex-wrap flex-row justify-content-center margin-top-bottom">
          {#each recordings as recording }
          <div class="recording my-3">
            <Keyword id={recording.id} 
                     bind:keyword={recording.keyword}
                       is_new={recording.is_new}
                       onRemoveClick={() => onRemoveClick(recording)}
                       onPlayClick={() => onPlayClick(recording)}
                       bind:selecting={recording.selecting}
                       />
          </div>
          {/each}
    </div>
  </Container>
  <div class="bottom-options d-flex flex-row justify-content-center">
      <div class="opt-container" on:click={onRecordClick}>
        <WaveBanner>
          <div class="opt-icon">
            <IoMdMicrophone/>
          </div>
        </WaveBanner>
      </div>

      <div class="opt-container" on:click={onSyncClick}>
        <WaveBanner>
          <div class="opt-icon">
            <FaSync/>
          </div>
        </WaveBanner>
      </div>
  </div>
{/if}
</div>

