
<script>
import { Spinner } from 'sveltestrap';
import { Container, Row, Col } from 'sveltestrap';
import Keyword from './Keyword.svelte';
import WaveBanner from "./../../banners/WaveBanner.svelte"
import IoMdMicrophone from 'svelte-icons/io/IoMdMicrophone.svelte'
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
      "selecting": false
    });

    is_recording = false;
    recordings = recordings;
  });
}

let captureEvent = (e) => {
  // If we are selecting something, just de-select
  if (recordings.some(v => v.selecting)) {
    recordings = recordings.map(v => {
      v.selecting = false;

      return v;
    })
    
    e.stopPropagation();
  // If we are syncing, do nothing and wait until sync is done
  // syncing should trigger a re-render of something else.
  } else if (is_syncing) {
    e.stopPropagation();

  // otherwise start syncing with friday
  } else {
    is_syncing = true;
    syncWithFriday();
    e.stopPropagation()
  }
}

async function syncWithFriday()  {
  let examples = {}
  recordings.forEach(recording => {
    if (recording.keyword != "") {
      examples[recording.id] = recording.keyword;
    }
  });

  await FridayAPI.setExamples(examples);
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
          }
        } else {
          return {
            "id": cid,
            "keyword": "",
            "selecting": false,
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

.top-separator {
   height: 100px;
}

.mic-icon {
  height: 60px;
}

.mic-icon:hover {
  opacity: 0.9;
  cursor: pointer;
}

.middle-screen {
  position: fixed;
  margin: 0 auto;
  top: 50%;
  left: 50%;

  /*To truly get it into the center*/
  transform: translate(-50%, -50%);
}

.mic-container {
  height: 100px;
  width: 120px;
}

.recording {
  position: relative;
  width: 350px;
  padding-right: 15px;
  padding-left: 15px;
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
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="top-separator"></div>
      </Col>
    </Row>
    <Row class="d-flex justify-content-center">
      <div class="mic-container" on:click={onRecordClick}>
        <WaveBanner>
          <div class="mic-icon">
            <IoMdMicrophone/>
          </div>
        </WaveBanner>
      </div>
    </Row>
    <div class="d-flex flex-wrap flex-row justify-content-center">
          {#each recordings as recording }
          <div class="recording my-3">
            <Keyword id={recording.id} 
                     bind:keyword={recording.keyword}
                       onRemoveClick={() => onRemoveClick(recording)}
                       onPlayClick={() => onPlayClick(recording)}
                       bind:selecting={recording.selecting}
                       />
          </div>
          {/each}
    </div>
  </Container>
{/if}
</div>

