import { FridayAPI } from "../FridayAPI";


export let commands = {};

export let initCommands = () => {
  return FridayAPI.getBoundScripts().then(bound => {
    commands = bound;
    return commands;
  });
}

