
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import {Col, Container, Row, Card} from 'sveltestrap';
import { FridayAPI } from "./../../FridayAPI.js"
import { Vendor } from "./../../Core.js"

// This function syncs a daction to friday
export let sync;
// The current action we're tinkering on
export let daction;


export let lights = [];
export let states = []

// Everything in this block is called on a change of our variables

let makeIntoHueAction = (localDAction) => {
    if (localDAction.vendor !== Vendor.hueLights) {
      localDAction.vendor = Vendor.hueLights;
      localDAction.command["id"] = 0;
      localDAction.command["state"] = {
        "on": false
      }
    }
}

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

.on-click:hover {
  cursor: pointer;
  opacity: 0.9;
}

.light {
  width: 100%;
  overflow: hidden;
}

.empty-space {
  height: 10px;
}

.horizontal-space {
  width: 10px;
}

</style>

<Container fluid>
  <Row> 
    <Col xs=6 sm=6 md=6 lg=6 > 
      {#each lights as light }
        <Row class="text-center">

          {#if light.active}
            <div class="full-width" on:click={(e) => e.stopPropagation()}>
                <Card color="primary">
                <div class="light card-header" {...light.props}> {light.name} </div>
                </Card>
              </div>
          {:else}
              <div class="on-click full-width"  on:click={(e) => updateLightID(e, light)}>
                <Card color="dark">
                <div  class="light card-header" {...light.props}> {light.name} </div>
                </Card>
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
            <div class="full-width" on:click={(e) => e.stopPropagation()}>
                <Card color="primary" class="ml-4">
                <div class="light card-header" {...state.props}> {state.name} </div>
                </Card>
              </div>
          {:else}
              <div class="on-click full-width "  on:click={(e) => updateLightState(e, state)}>
                <Card color="dark" class="ml-4">
                <div  class="light card-header" {...state.props}> {state.name} </div>
                </Card>
              </div>
          {/if}
          </Row>
          <div class="empty-space"></div>
        {/each}
    </Col>

  </Row>
</Container>
