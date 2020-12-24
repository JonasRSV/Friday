function removeItemOnce(arr, value) {
  var index = arr.indexOf(value);
  if (index > -1) {
    arr.splice(index, 1);
  }
  return arr;
}

r = new FridayAPI()
commandFactory = new CommandFactory();


class PhilipsHueUI {

  constructor() {
    this.command_state = null;
    this.classes = null;
    this.lights = null;

  }

  onClassClick(ev, command_state, elem, shared_name, name, action) {
    command_state[shared_name.name] = removeItemOnce(
      command_state[shared_name.name], action)

    if (command_state[shared_name.name].length == 0) {
      delete command_state[shared_name.name]
    }

    if (command_state[name] != null) {
      command_state[name].push(action)
    } else {
      command_state[name] = [action]
    }

    elem.textContent = name;
    shared_name.name = name;

    // Sends to Assistant
    r.set_lights_commands(
      command_state,
      (err) => console.log("Failed to update commnads!", err),
      (_) => console.log("Updated commands!")
    )

  }

  onLampClick(ev, command_state, elem, shared_name, action, next_id) {
    action.id = next_id;
    elem.textContent = next_id;

    // Sends to commands to Assistant
    r.set_lights_commands(
      command_state,
      (err) => console.log("Failed to update commnads!", err),
      (_) => console.log("Updated commands!")
    )

  }

  onStateClick(ev, command_state, elem, shared_name, action, next_state) {
    action.state.on = next_state === "💡"
    elem.textContent = next_state;

    // Sends to Assistant
    r.set_lights_commands(
      command_state,
      (err) => console.log("Failed to update commnads!", err),
      (_) => console.log("Updated commands!")
    )

    r.set_lights([action],
      (_) => console.log("Failed to send light update"),
      (_) => console.log("Updated light!")
    )
  }

  addCommand() {
    // I wish for noone to try to understand why 
    // This code is the way it is..
    // It got this way because I just wanted to implement a UI
    // quickly.. and I am not a webdeveloper.. and decided hey
    // lets just do with without any frameworks.. and shortcuts
    // after shortcuts lead to this monstrosity..
    // Ill just build something with a framework at some point in the future


    // duplicate some entry..
    // if they have none.. tough luck.. this UI sux! :) 
    // Will have to build a UI using some reasonable framework in the future
    // building something larger in vanilla JS was not as fun as I had 
    // initially imagined.. tbf nothing wrong with vanilla JS actually
    // just web-developing that is not my forte... Where are my types!

    var entries = Object.entries(this.command_state)
    var entry_name = entries[0][0]

    // Apparently this is how you clone stuff in JS
    var action = JSON.parse(JSON.stringify(this.command_state[entry_name][0]))

    // Now we duplicate this in the command state so that it is as if it exists
    this.command_state[entry_name].push(action)

    commandFactory.make_command(
      this.command_state,
      entry_name,
      this.classes,
      [action],
      this.lights,
      this.onClassClick,
      this.onLampClick,
      this.onStateClick,
      this.removeCommand
    )


  }

  removeCommand(ev, command_state, entry, shared_name, action) {
    // Remove from commands
    command_state[shared_name.name] = removeItemOnce(command_state[shared_name.name], action)

    // Remove from DOM
    entry.parentNode.removeChild(entry)

    // Updates Assistant
    r.set_lights_commands(
      command_state,
      (err) => console.log("Failed to update commnads!", err),
      (_) => console.log("Updated commands!")
    )

  }

  render_light_commands_on_server() {
    r.get_model_classes(
      err => console.log("Failed to get model classes"),
      classes => {
        r.get_lights(
          err => console.log("Failed to get lights"),
          lights => {
            r.get_lights_commands(
              err => console.log("Failed to get light commands"),
              commands => {
                console.log("Commands", commands)
                this.command_state = commands;
                console.log(this.command_state)
                this.classes = classes;
                this.lights = lights;

                Object.entries(commands).forEach((entry) =>
                  commandFactory.make_command(
                    commands,
                    entry[0], 
                    classes,
                    entry[1],
                    lights,
                    this.onClassClick,
                    this.onLampClick,
                    this.onStateClick,
                    this.removeCommand
                  ))
              })
          })
      })
  }

  run() {
    this.render_light_commands_on_server();
    document.getElementById("add-button").onclick = () => this.addCommand();

  }
}

controller = new PhilipsHueUI();
controller.run();


//r.get_login_status(
//(_) => {
  //console.log("Is logged in!");
//},
//(err) => {
  //console.log("Is Not logged in " + err.status)
//})


//r.login(
//(_) => {
  //console.log("logged in!");
//},
//(err) => {
  //console.log("Failed to login " + err.status)
//})
