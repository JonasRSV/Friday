let name = "";
import { FridayAPI } from "../FridayAPI";

export let initDevice = () => {
  return FridayAPI.getDeviceName().then(n => {
    console.log("device name", n);
    name = n;

    return "ok";
  });
}

export let getName = () => {
  return name;
}
