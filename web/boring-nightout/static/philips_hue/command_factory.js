function makeId(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function setupNameSelector(
  entry, 
  shared_name, 
  names, 
  command_state, 
  action,
  onNameClick) {
    // Displayed command 
    var name_elem = entry.querySelector(".command-name");
    name_elem.textContent = shared_name.name;

    // Setup Name selector
    var name_drop_down = entry.querySelector(".name-dropdown");
    var item_template = name_drop_down.querySelector(".dropdown-item");

    // Make it visible
    item_template.style = "color: green;";

    names.slice(1, names.length).forEach((name) => {
        var name_entry = item_template.cloneNode(true);

        name_entry.textContent = name;
        name_drop_down.appendChild(name_entry);

        name_entry.onclick = (ev) => onNameClick(
            ev,
            command_state,
            name_elem,
            shared_name,
            name,
            action);
    });
}

function setupLampSelector(
  entry, 
  shared_name, 
  action, 
  lights, 
  command_state,
  onLampClick) {
    var lamp_elem = entry.querySelector(".command-lamp")
    lamp_elem.textContent = action.id;

    // Setup Lamp selector
    var lamp_drop_down = entry.querySelector(".lamp-dropdown");
    var item_template = lamp_drop_down.querySelector(".dropdown-item");

    // Make it visible
    item_template.style = "color: red;";

    lights.forEach(light => {
        var lamp_entry = item_template.cloneNode(true);

        lamp_entry.textContent = light.id;
        lamp_drop_down.appendChild(lamp_entry);

        lamp_entry.onclick = (ev) => onLampClick(
            ev,
            command_state,
            lamp_elem,
            shared_name,
            action,
            light.id);
    });
}

function setupStateSelector(
  entry, 
  shared_name, 
  action, 
  command_state,
  onStateClick) {
    var state_elem = entry.querySelector(".command-state")
    if (action.state.on) {
        state_elem.textContent = "💡";
    } else {
        state_elem.textContent = "❌";
    }

    // Setup state selector
    var state_drop_down = entry.querySelector(".state-dropdown");
    var item_template = state_drop_down.querySelector(".dropdown-item");

    // Make it visible
    item_template.style = "";

    ["💡", "❌"].forEach(state => {
        var state_entry = item_template.cloneNode(true);

        state_entry.textContent = state;
        state_drop_down.appendChild(state_entry);

        state_entry.onclick = (ev) => onStateClick(
            ev,
            command_state,
            state_elem,
            shared_name,
            action,
            state);
    });
}

class CommandFactory {
  constructor () {
    this.container = document.getElementById("command-container");
    this.template = document.getElementById("command-template");
  }

  make_command(
        command_state,
        name,
        names,
        actions,
        lights,
        onNameClick,
        onLampClick,
        onStateClick,
        onRemoveClick
    ) {

      var shared_name = {
        "name": name
      }


        actions.forEach(action => {

            var entry = this.template.cloneNode(true);
            entry.id = makeId(10); // To keep IDs unique


            setupNameSelector(
                entry,
                shared_name,
                names,
                command_state,
                action,
                onNameClick
            )

            setupLampSelector(
                entry,
                shared_name,
                action,
                lights,
                command_state,
                onLampClick
            )

            setupStateSelector(
                entry,
                shared_name,
                action,
                command_state,
                onStateClick
            )

            var remove_button = entry.querySelector(".command-remove");

            remove_button.onclick = (ev) => onRemoveClick(
              ev,
              command_state,
              entry,
              shared_name,
              action);


            // make it visible
            entry.style = "";

            this.container.appendChild(entry);

        });
    }

}
