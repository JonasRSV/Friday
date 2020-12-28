function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

export class dAction {
    static New() {
        return new dAction("", "", {});
    }

    constructor(name, vendor, command) {
        // ID is for svelte 
        this.id = makeid(10);

        // Reference to component that renders this action
        this.component = null;

        this.name = name;
        this.vendor = vendor;
        this.command = command;
    }

    setName(name) {
        if (this.component != null) {
            // The component will set the value 
            // of this and also update the UI
            this.component.setName(name)
        } else {
            this.name = name
        }
    }

    setCommand(command) {
        if (this.component != null) {
            // The component will set the value 
            // of this and also update the UI
            this.component.setCommand(command)
        } else {
            this.command = command
        }
    }
}
