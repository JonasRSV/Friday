
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import {Col, Container, Row} from 'sveltestrap';
import { FridayAPI } from "./../../FridayAPI.js"
import { Vendor } from "./../../Core.js"
import BubbleBanner from "./../../banners/BubbleBanner.svelte"
import GreenBubbleBanner from "./../../banners/GreenBubbleBanner.svelte"

// This function syncs a daction to friday
export let sync;
// The current action we're tinkering on
export let daction;


export let lights = [];
export let states = []


let makeIntoHueAction = (localDAction) => {
    if (localDAction.vendor !== Vendor.hueLights) {
      localDAction.vendor = Vendor.hueLights;
      localDAction.command["id"] = 0;
      localDAction.command["state"] = {
        "on": false
      }
    }
}

// Everything in this block is called on a change of our variables
$: {
  console.log("Re-rendered")
  if (daction != null) {
    // If command is not yet a hueLights command - we make it into one 

  // Get available lights 
  FridayAPI.getHueLights().then(dlights => {
      // Full lights list to render all available lights
      lights = dlights.map(light => {
        return {
          "name": light.id + " - " + light.name,
          "id": light.id,
          "active": light.id == daction.command.id,
          "props": { }
        }
      })

    // Set the state of the currently active light

      if (daction.vendor == Vendor.hueLights) {
        states = [
          {
            "name": "On",
            "active": daction.command.state.on,
            "props": {
            }
          },
          {
            "name": "Off",
            "active": !daction.command.state.on,
            "props": { }
          }
        ]
      } else {
        states = [
          {
            "name": "On",
            "active": false,
            "props": {
            }
          },
          {
            "name": "Off",
            "active": false,
            "props": { }
          }
        ]
      }
    })

  }
}

let updateLightID = (e, light) => {
  // Make sure onClick is not passed to parent
  e.stopPropagation();

  // Makes it into a hue action if it isn't one.
  makeIntoHueAction(daction)

  daction.command.id = light.id;
  daction.setCommand(daction.command)

  // Re-renders
  daction = daction

  // Sync action to friday
  sync(daction);

  // Update this light to the state
  // (This works as long as it is a hue command)
  FridayAPI.setHueLights([daction.command])

}

let updateLightState = (e, state) => {
  console.log("Updated light state")
  // Make sure onClick is not passed to parent
  e.stopPropagation();

  // Makes it into a hue action if it isn't one.
  makeIntoHueAction(daction)

  daction.command.state.on = state.name == "On";
  daction.setCommand(daction.command)

  // Re-renders
  daction = daction

  // Sync action to friday
  sync(daction);

  // Update this light to the state
  // (This works as long as it is a hue command)
  FridayAPI.setHueLights([daction.command])
}


</script>


<style>


.full-width {
  width: 100%;
}

.empty-space {
  height: 10px;
}


.block {
  height: 80px;
  display: flex;
  justify-content: center;
  flex-direction: row;
}

.block-name {
  height: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  font-size: 18pt;
}

.opacity-hover {
  width: 100%;
  height: 100%;
}

.opacity-hover:hover {
  cursor: pointer;
  opacity: 0.8;
}


.title-text {
  font-size: 22pt;
}

</style>

<Container fluid>
  <Row> 
    <Col xs=1 sm=1 md=1 lg=1> </Col>
    <Col xs=5 sm=4 md=4 lg=4> 
      <Row>
        <Col xs=12 sm=12 md=12 lg=12>
          <div class="title-text">Set...</div>
        </Col>
      </Row>
      <Row>
        <div class="empty-space"></div>
      </Row>
      {#each lights as light }
        <Row class="text-center">

          {#if light.active}
            <GreenBubbleBanner>
              <div class="block full-width" on:click={(e) => e.stopPropagation()}>
                <div class="block-name"> {light.name} </div>
              </div>
            </GreenBubbleBanner>
          {:else}
            <div class="opacity-hover">
              <BubbleBanner>
                <div class="block full-width"  on:click={(e) => updateLightID(e, light)}>
                  <div class="block-name"> {light.name} </div>
                </div>
              </BubbleBanner>
            </div>
          {/if}
          </Row>
          <div class="empty-space"></div>
        {/each}
    </Col>

    <Col xs=1 sm=2 md=2 lg=2> </Col>

    <Col xs=4 sm=4 md=4 lg=4> 
      <Col xs=12 sm=12 md=12 lg=12>
        <div class="title-text">To...</div>
      </Col>
      <Row>
        <div class="empty-space"></div>
      </Row>
      {#each states as state }
        <Row class="text-center">

          {#if state.active}
            <GreenBubbleBanner>
              <div class="block full-width" on:click={(e) => e.stopPropagation()}>
                <div class="block-name"> {state.name} </div>
              </div>
            </GreenBubbleBanner>
          {:else}
            <div class="opacity-hover">
              <BubbleBanner>
                <div class="block full-width "  on:click={(e) => updateLightState(e, state)}>
                  <div class="block-name"> {state.name} </div>
                </div>
              </BubbleBanner>
            </div>
          {/if}
          </Row>
          <div class="empty-space"></div>
        {/each}
    </Col>
    <Col xs=1 sm=1 md=1 lg=1> </Col>

  </Row>
</Container>
