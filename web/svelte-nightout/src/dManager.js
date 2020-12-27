export const Vendor = Object.freeze({
    "hue": "hue",
});


function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}



class Update {
    constructor(vendor, command) {
        this.vendor = vendor
        this.command = command
    }
}

class Mapping {
    constructor(name, updates) {
        this.name = name;
        this.updates = updates;
    }

    add(vendor, commands) {
        commands.forEach(command => {
            this.updates.push(
                new Update(vendor, command)
            );
        });
    }
}

export class dAction {
    constructor(name, update) {
        // ID is for svelte 
        this.id = makeid(10);

        // Reference to component that renders this action
        this.component = null;

        this.name = name;
        this.update = update;
    }

    has_hue() {
        return update.name == Vendor.hue;
    }
}


export class dManager {

    constructor() {
        this.mappings = {}
    }

    update_hue_lights(hue_actions) {
        for (const [key, value] of Object.entries(hue_actions)) {
            if (!(key in this.mappings)) {
                this.mappings[key] = new Mapping(key, []);
            }

            this.mappings[key].add(Vendor.hue, value)
        }
    }

    get_actions() {
        return Object.values(this.mappings).flatMap(
            v => v.updates.flatMap(u => new dAction(v.name, u)));
    }
}
