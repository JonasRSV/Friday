
<script>
// This Component is used to modify Actions
// It is a Action mechanic!
import {Col, Container, Row, ListGroup, ListGroupItem} from 'sveltestrap';
import { FridayAPI } from "./FridayAPI.js"
import { Vendor } from "./Core.js"

// TODO:
// TODO
// TODO:
// TODO: This entire component needs a make-over
// Currently it is hard-logiced for hue 
// The purpose of this component is to take a 'daction' object
// let users pick attributes and then use the 'daction' objects
// API to update. The daction object will make sure that the
// UI is updated and that Friday gets updated
// This component also has access to 'FridayAPI' to get data.
// So this component should fetch data using FridayAPI
// and reflect updates using the provided daction.


// This function syncs a daction to friday
export let sync;
// If this component is active or not
export let active;
// The current action we're tinkering on
export let daction;


// TODO: These should probably be removed in the future?
export let names = [];
export let hueLights = [];
export let hueLightsStates = []

// Everything in this block is called on a change of our variables
$: {
  if (active && daction != null) {
    // if we get an action that has no commands - we make it into a hue action
    // TODO: .. in the future we should not

    // So yeah this should be removed.. 'javascript'
    if (JSON.stringify(daction.command) === '{}') {
      daction.command["id"] = 0;
      daction.command["state"] = {
        "on": false
      }
      daction["vendor"] = "hueLights";
      console.log("Got empty action")
    }


  // Get available names and put them in a list
  FridayAPI.names().then(availableNames => {
    names = availableNames.map(name => {
      let conf = {
        "value": name,
        "props": {
          "class" : "list-group-item-dark",
          "action": true,
          "tag": "a"
        }
      }

      if (name == daction.name) {
        conf["props"]["active"] = true;
        conf["props"]["action"] = false;
      }

      return conf;
    })
  })

  // Get available lights and put them in a list
  FridayAPI.getHueLights().then(lights => {
      hueLights = lights.map(light => {
        let conf = {
          "value": light.id + " - " + light.name,
          "id": light.id,
          "props": {
            "class" : "list-group-item-dark",
            "action": true,
            "tag": "a"
          }
        }

        if (daction.vendor == Vendor.hueLights) {
          // For this light we also update the states
          if (light.id == daction.command.id) {
            conf["props"]["active"] = true;
            conf["props"]["action"] = false;
          }

          hueLightsStates = [
            {
              "value": "On",
              "props": {
                "class": "list-group-item-dark",
                "active": daction.command.state.on,
                "action": !daction.command.state.on,
                "tag": "a"
              }
            },
            {
              "value": "Off",
              "props": {
                "class" : "list-group-item-dark",
                "active": !daction.command.state.on,
                "action": daction.command.state.on,
                "tag": "a"
              }
            }
          ]
        }

        return conf;
      })
    })
  }
}

let updateName = (e, name) => {
  // Make sure onClick is not passed to parent
  e.stopPropagation();

  daction.setName(name.value)

  // Re-renders
  daction = daction

  // Sync action to friday
  sync(daction);
}

let updateLightID = (e, lightID) => {
  // Make sure onClick is not passed to parent
  e.stopPropagation();

  daction.command.id = lightID.id;
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
  // Make sure onClick is not passed to parent
  e.stopPropagation();

  daction.command.state.on = state.value == "On";
  daction.setCommand(daction.command)

  // Re-renders
  daction = daction

  // Sync action to friday
  sync(daction);

  // Update this light to the state
  // (This works as long as it is a hue command)
  FridayAPI.setHueLights([daction.command])
}

let deactivate = () => {
  active = false;
}

</script>


<style>



.fixed-above {
  position: fixed;
  width: 100%;
  height: 100%;
  background-color: rgba(5, 5, 5, 0.9);
  top: 0px;
  left: 0px;

  display: flex;
  flex-direction: column;
  justify-content: center;
}

.on-click:hover {
  cursor: pointer;
}

/*# TODO: Get rid of these somehow..*/
:global(.list-group-item:hover) {
  cursor: pointer;
}

:global(.active:hover) {
  cursor: default;
}

</style>

{#if active}
  <div class="fixed-above" on:click={deactivate} >
<Container fluid class=container-xs>
  <Row> 
    <Col xs=0 sm=0 md=0 lg=0> </Col>
      <Col xs=4 sm=4 md=4 lg=4 > 
        <ListGroup>
          {#each names as name }
            {#if name.props.active}
            <div class="on-click"  on:click={(e) => e.stopPropagation()}>
              <ListGroupItem {...name.props}> {name.value} </ListGroupItem>
            </div>
            {:else}
            <div class="on-click"  on:click={(e) => updateName(e, name)}>
              <ListGroupItem {...name.props}> {name.value} </ListGroupItem>
            </div>
            {/if}
          {/each}
        </ListGroup>
      </Col>

      <Col xs=4 sm=4 md=4 lg=4 > 
        <ListGroup>
          {#each hueLights as light }
            {#if light.props.active}
            <div class="on-click"  on:click={(e) => e.stopPropagation()}>
              <ListGroupItem {...light.props}> {light.value} </ListGroupItem>
            </div>
            {:else}
            <div class="on-click"  on:click={(e) => updateLightID(e, light)}>
              <ListGroupItem {...light.props}> {light.value} </ListGroupItem>
            </div>
            {/if}
          {/each}
        </ListGroup>
      </Col>

      <Col xs=4 sm=4 md=4 lg=4 > 
        <ListGroup>
          {#each hueLightsStates as state }
            {#if state.props.active}
            <div class="on-click"  on:click={(e) => e.stopPropagation()}>
              <ListGroupItem {...state.props}> {state.value} </ListGroupItem>
            </div>
            {:else}
              <div class="on-click"  on:click={(e) => updateLightState(e, state)}>
                <ListGroupItem {...state.props}> {state.value} </ListGroupItem>
              </div>
            {/if}
          {/each}
        </ListGroup>
      </Col>

    <Col xs=0 sm=0 md=0 lg=0> </Col>
  </Row>
</Container>
</div>
{/if}
