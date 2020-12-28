import Lamp from "./icons/Lamp.svelte"
import Unknown from "./icons/Unknown.svelte"
import LampID from "./icons/LampID.svelte"
import { Vendor } from "../Core.js"



function lookupHueLights(daction) {
  let icons = []
  icons.push({
    "component": LampID,
    "props": {
      "number": daction.command.id,
    }
  })

  if (daction.command.state.on) {
    icons.push({
      "component": Lamp,
      "props": {
        "on": true
      }
    })
  } else {
    icons.push({
      "component": Lamp,
      "props": {
        "on": false
      }
    })
  }

  return icons;
}

export class IconLookup {
  // This is a Action.js / Update
  // Really wish there were types :(
  static lookup(daction) {

    if (daction.vendor == Vendor.hueLights) {
      return lookupHueLights(daction);
    }

    // List of components and props
    return [ 
      {
        "component": Unknown, 
        "props": {} 
      }
    ]
  }
}
