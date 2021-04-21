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
            if (!(action.keyword in lightsResponse)) {
                lightsResponse[action.keyword] = []
            }

            lightsResponse[action.keyword].push(action.command)
        }
    });


    return JSON.stringify(lightsResponse);
}

export function hueLightsToDActions(lights) {
    let dactions = []
    for (const [keyword, commands] of Object.entries(lights)) {
        commands.forEach((command) => {
            dactions.push(new dAction(keyword, Vendor.hueLights, command))
        });
    }
    return dactions;
}
