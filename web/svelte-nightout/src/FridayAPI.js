import {
    ActiondActionBi
} from "./Core.js";
import {
    APInames
} from "./api/Names.js";
import {
    APIGetHueLights,
    APISetHueLights,
    APIGetHueLightsCommands,
    APISetHueLightsCommands
} from "./api/HueLights.js";


export class FridayAPI {
    // TODO: how to do this better?
    // For dev
    //static prefix = "http://0.0.0.0:8000";
    // For production
    static prefix = "";

    // Gets the names of the command e.g 'on' - 'off' etc
    static names = () => APInames(this.prefix);

    // Gets the hue lights available 
    // See philips hue /lights endpoint for documentation of content
    static getHueLights = () => APIGetHueLights(this.prefix);
    static setHueLights = (data) => APISetHueLights(this.prefix, JSON.stringify(data));


    // Gets the hueLightCommands and converts them to our representation of commands
    static getHueLightsCommands = () => APIGetHueLightsCommands(this.prefix)
        .then(ActiondActionBi.hueLightsToDActions)

    // Sets the hueLightCommands 
    static setHueLightsCommands = (dactions) => APISetHueLightsCommands(
        this.prefix,
        ActiondActionBi.dActionsToHueLights(dactions)
    )

    static async fetchActions() {
        let dactions = [];
        dactions.push(...await this.getHueLightsCommands());

        return dactions;
    }
}
