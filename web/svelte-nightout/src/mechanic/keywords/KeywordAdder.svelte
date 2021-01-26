
<script>
import { Container, Row, Col } from 'sveltestrap';
import Recording from './Recording.svelte';
import NameInput from './NameInput.svelte';
import MicrophoneBanner from './MicrophoneBanner.svelte';
import IoMdMicrophone from 'svelte-icons/io/IoMdMicrophone.svelte'
import { FridayAPI } from "./../../FridayAPI.js"
import { playAudio } from "./../../core/Audio";
import { onMount } from "svelte";


let recordingsIDs = []
let name = "";

let onRemoveClick = (state) => {
  state.selecting = false;

  recordingsIDs = recordingsIDs.filter(v => v.id != state.id);

  // Remove recording on device
  FridayAPI.recordingRemove(state.id);

  recordingsIDs = recordingsIDs;
}

let onSelectClick = (state) => {
  state.selecting = false;
  state.selected = !state.selected;

  console.log("Selecting", state.id);

  recordingsIDs = recordingsIDs;
}

let onRename = (state, newId) => {
  state.selecting = false;

  // Rename recording on device
  FridayAPI.recordingRename(state.id, newId);

  // Rename recording in UI
  state.id = newId;

  recordingsIDs = recordingsIDs;
}

let onPlayClick = (state) => {
  state.selecting = false;
  console.log("Playing", state.id);

  // Rename recording on device
  FridayAPI.recordingAudio(state.id).then(audio => playAudio(audio));

  recordingsIDs = recordingsIDs;
}

let onRecordClick = (e) => {
  e.stopPropagation();

  // Rename recording on device
  FridayAPI.recordingNew().then(recording => {
    recordingsIDs.push({
      "id": recording.id,
      "selecting": false,
      "selected": false
    });

    recordingsIDs = recordingsIDs;
  });

  console.log("recording");

}

let captureIfSelecting = (e) => {
  if (recordingsIDs.some(v => v.selecting)) {
    recordingsIDs = recordingsIDs.map(v => {
      v.selecting = false;

      return v;
    })
    
    e.stopPropagation();
  }
}

let onComplete = () => {
  console.log("Adding Keyword", name)
}

onMount (async () => { 
  FridayAPI.recordingClips().then(clips => {
    recordingsIDs = clips.ids.map(c => {
      return {
        "id": c,
        "selecting": false,
        "selected": false
      }
    });
  });
});

</script>


<style>



.empty-space {
  height: 10px;
}

.keyword-adder-keypress-capture {
  position: fixed;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.0);
  top: 0px;
  left: 0px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: scroll;
}

.mic-separator {
   height: 100px;
}

.mic-icon {
  height: 60px;
}

.mic-icon:hover {
  opacity: 0.9;
  cursor: pointer;
}

</style>


<div class="keyword-adder-keypress-capture" on:click={captureIfSelecting}>
<Container fluid class="keyword-adder">
  <Row> 
      <Col xs=6 sm=6 md=6 lg=6>
      {#each recordingsIDs as recording }
        <Recording id={recording.id} 
                   onRemoveClick={() => onRemoveClick(recording)}
                   onSelectClick={() => onSelectClick(recording)}
                   onPlayClick={() => onPlayClick(recording)}
                   onRename={(newId) => onRename(recording, newId)}
                   bind:selecting={recording.selecting}
                   bind:selected={recording.selected}
                   />
        <div class="empty-space"></div>
      {/each}
      </Col >
      <Col xs=6 sm=6 md=6 lg=6>
      <NameInput 
        onComplete={onComplete}
        bind:name={name}/>
      </Col>
  </Row>

  <Row> 
    <Col xs=12 sm=12 md=12 lg=12>
      <div class="mic-separator"></div>
    </Col>
  </Row>
  <Row> 
    <Col xs=4 sm=4 md=4 lg=4/>
    <Col xs=4 sm=4 md=4 lg=4>
      <div on:click={onRecordClick}>
        <MicrophoneBanner>
          <div class="mic-icon">
            <IoMdMicrophone/>
          </div>
        </MicrophoneBanner>
      </div>
    </Col>
    <Col xs=4 sm=4 md=4 lg=4/>
  </Row>
</Container>
</div>

