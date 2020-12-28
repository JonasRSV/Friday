import {
    Vendor
} from "./core/Vendor.js";
import {
    hueLightsToDActions,
    dActionsToHueLights
} from "./core/HueLights.js";



export {
    Vendor
}
from "./core/Vendor";


export {
    dAction

}
from "./core/dAction";


// This class is a bijection between
// actions from the API and the class dAction 
export class ActiondActionBi {
    static hueLightsToDActions = hueLightsToDActions
    static dActionsToHueLights = dActionsToHueLights
}
