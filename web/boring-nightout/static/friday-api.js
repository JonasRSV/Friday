class FridayAPI {
  constructor() {
    this.base =  "http://" + window.location.host; 
  }

  get(url, callback) {
    var xhttp = new XMLHttpRequest(); 

    xhttp.onreadystatechange = () => {
      if (xhttp.readyState == 4) {
        callback(xhttp);
      }
    }

    xhttp.open("GET", this.base + url, true);
    xhttp.send()
  }

  post(url, callback, data) {
    var xhttp = new XMLHttpRequest(); 

    xhttp.onreadystatechange = () => {
      if (xhttp.readyState == 4) {
        callback(xhttp);
      }
    }

    xhttp.open("GET", this.base + url, true);
    xhttp.setRequestHeader("Content-Type", "application/json")
    xhttp.send(JSON.stringify(data))
  }

  put(url, callback, data) {
    var xhttp = new XMLHttpRequest(); 

    xhttp.onreadystatechange = () => {
      if (xhttp.readyState == 4) {
        callback(xhttp);
      }
    }

    xhttp.open("PUT", this.base + url, true);
    xhttp.setRequestHeader("Content-Type", "application/json")
    xhttp.send(JSON.stringify(data))
  }


  // Model API
  get_model_classes(failure_callback, success_callback) {
    this.get("/friday-inference/tensorflow-models/discriminative/classes",
      (response) => {
        if (response.status == 200) {
          success_callback(JSON.parse(response.response))
        } else {
          failure_callback(response)
        }
      })
  }

  get_model_sensitivity(failure_callback, success_callback) {
    this.get("/friday-inference/tensorflow-models/discriminative/sensitivity",
      (response) => {
        if (response.status == 200) {
          success_callback(JSON.parse(response.response))
        } else {
          failure_callback(response)
        }
      })
  }

  // Hue API

  get_lights_commands(failure_callback, success_callback) {
    this.get("/friday-vendor/philips-hue/lights/commands",
      (response) => {
        if (response.status == 200) {
          success_callback(JSON.parse(response.response))
        } else {
          failure_callback(response)
        }
      })
  }

  set_lights_commands(lights_commands, failure_callback, success_callback) {
    this.put("/friday-vendor/philips-hue/lights/commands",
      (response) => {
        if (response.status == 200) {
          success_callback(true)
        } else {
          failure_callback(response)
        }
      }, lights_commands)
  }

  get_lights(failure_callback, success_callback) {
    this.get("/friday-vendor/philips-hue/lights",
      (response) => {
        if (response.status == 200) {
          success_callback(JSON.parse(response.response))
        } else {
          failure_callback(response)
        }
      })
  }

  set_lights(light_updates, failure_callback, success_callback) {
    this.put("/friday-vendor/philips-hue/lights",
      (response) => {
        if (response.status == 200) {
          success_callback(true)
        } else {
          failure_callback(response)
        }
      }, light_updates)
  }

  get_login_status(failure_callback, success_callback) {
    this.get("/friday-vendor/philips-hue/login",
      (response) => {
        if (response.status == 200) {
          success_callback(true)
        } else {
          failure_callback(response)
        }
      })
  }

  login(failure_callback, success_callback) {
    this.put("/friday-vendor/philips-hue/login",
      (response) => {
        if (response.status == 200) {
          success_callback(true)
        } else {
          failure_callback(response)
        }
      }, null)
  }

}
