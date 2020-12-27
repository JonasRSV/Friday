// TODO: how to do this better?
// For dev
const prefix = "http://0.0.0.0:8000";
// For production
/*const prefix = "";*/

export class API {

  constructor (dmanager) {
    this.dmanager = dmanager;
  }

  async hue_lights() {
    await fetch(
      prefix + "/friday-vendor/philips-hue/lights/commands")
      .then(r => {
        if (r.status == 200) {
          return r.json()
        } else {
          return {}
        }
      })
      .then((hue) => this.dmanager.update_hue_lights(hue));
  }

  async fetch_actions() {
    await this.hue_lights()
  }
}
