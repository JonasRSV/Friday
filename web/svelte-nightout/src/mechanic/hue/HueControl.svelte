
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import {Col, Container, Row, Card} from 'sveltestrap';
import { FridayAPI } from "./../../FridayAPI.js"
import { Vendor } from "./../../Core.js"
import CogsBanner from "./../../banners/CogsBanner.svelte"
import GreenCogsBanner from "./../../banners/GreenCogsBanner.svelte"

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
  height: 50px;
  display: flex;
  justify-content: center;
  flex-direction: row;
}

.block-name {
  height: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
}

.opacity-hover {
  width: 100%;
  height: 100%;
}

.opacity-hover:hover {
  cursor: pointer;
  opacity: 0.8;
}


</style>

<Container fluid>
  <Row> 
    <Col xs=6 sm=6 md=6 lg=6 > 
      {#each lights as light }
        <Row class="text-center">

          {#if light.active}
            <GreenCogsBanner>
              <div class="block full-width" on:click={(e) => e.stopPropagation()}>
                <div class="block-name"> {light.name} </div>
              </div>
            </GreenCogsBanner>
          {:else}
            <div class="opacity-hover">
              <CogsBanner>
                <div class="block full-width"  on:click={(e) => updateLightID(e, light)}>
                  <div class="block-name"> {light.name} </div>
                </div>
              </CogsBanner>
            </div>
          {/if}
          </Row>
          <div class="empty-space"></div>
        {/each}
    </Col>


    <Col xs=6 sm=6 md=6 lg=6  > 
      {#each states as state }
        <Row class="text-center">

          {#if state.active}
            <GreenCogsBanner>
              <div class="block full-width" on:click={(e) => e.stopPropagation()}>
                <div class="block-name"> {state.name} </div>
              </div>
            </GreenCogsBanner>
          {:else}
            <div class="opacity-hover">
              <CogsBanner>
                <div class="block full-width "  on:click={(e) => updateLightState(e, state)}>
                  <div class="block-name"> {state.name} </div>
                </div>
              </CogsBanner>
            </div>
          {/if}
          </Row>
          <div class="empty-space"></div>
        {/each}
    </Col>

  </Row>
</Container>
