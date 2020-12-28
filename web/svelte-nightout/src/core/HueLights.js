import {
    dAction
} from "./dAction";

import {
    Vendor
} from "./Vendor.js";

export function dActionsToHueLights(dactions) {
    let lightsResponse = {}

    dactions.forEach(action => {
        if (action.vendor == Vendor.hueLights) {
            if (!(action.name in lightsResponse)) {
                lightsResponse[action.name] = []
            }

            lightsResponse[action.name].push(action.command)
        }
    });


    return JSON.stringify(lightsResponse);
}

export function hueLightsToDActions(lights) {
    let dactions = []
    for (const [name, commands] of Object.entries(lights)) {
        commands.forEach((command) => {
            dactions.push(new dAction(name, Vendor.hueLights, command))
        });
    }
    return dactions;
}
