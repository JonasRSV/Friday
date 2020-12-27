import Lamp from "./icons/Lamp.svelte"
import Unknown from "./icons/Unknown.svelte"
import LampID from "./icons/LampID.svelte"
import { Vendor } from "../dManager.js"



class HueLookup {
  static lookup(update) {
    let icons = []
    icons.push({
      "component": LampID,
      "props": {
        "number": update.command.id,
      }
    })

    if (update.command.state.on) {
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
}

export class IconLookup {
  // This is a Action.js / Update
  // Really wish there were types :(
  static lookup(update) {

    if (update.vendor = Vendor.hue) {
      return HueLookup.lookup(update);
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
