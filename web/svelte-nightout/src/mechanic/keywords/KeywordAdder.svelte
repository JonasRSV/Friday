
<script>
import { Container, Row, Col } from 'sveltestrap';
import Recording from './Recording.svelte';
import NameInput from './NameInput.svelte';
import WaveBanner from "./../../banners/WaveBanner.svelte"
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
  justify-content: flex-start;
  overflow: scroll;
}

.top-separator {
   height: 100px;
}

.separator {
   height: 30px;
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
  <Container fluid>
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="top-separator"></div>
      </Col>
    </Row>
    <Row>
      <Col xs=0 sm=3 md=3 lg=3/>
      <Col xs=12 sm=6 md=6 lg=6>
        <NameInput 
          onComplete={onComplete}
          bind:name={name}/>
      </Col>
      <Col xs=0 sm=3 md=3 lg=3/>
    </Row>
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="separator"></div>
      </Col>
    </Row>
    <Row>
      <Col xs=0 sm=3 md=3 lg=3/>
      <Col xs=12 sm=6 md=6 lg=6>
        <div on:click={onRecordClick}>
          <WaveBanner>
            <div class="mic-icon">
              <IoMdMicrophone/>
            </div>
          </WaveBanner>
        </div>
      </Col>
      <Col xs=0 sm=3 md=3 lg=3/>
    </Row>
    <Row> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="separator"></div>
      </Col>
    </Row>
    <Row> 
      <Col xs=0 sm=2 md=2 lg=2/>
      <Col xs=12 sm=8 md=8 lg=8>
        <div class="keyword-container">
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
        </div>
      </Col>
      <Col xs=0 sm=2 md=2 lg=2/>
    </Row>
  </Container>
</div>

