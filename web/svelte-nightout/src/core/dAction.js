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

    constructor(keyword, vendor, command) {
        // ID is for svelte 
        this.id = makeid(10);

        // Reference to component that renders this action
        this.component = null;

        this.keyword = keyword;
        this.vendor = vendor;
        this.command = command;
    }

    setKeyword(keyword) {
        if (this.component != null) {
            // The component will set the value 
            // of this and also update the UI
            this.component.setKeyword(keyword)
        } else {
            this.keyword = keyword
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
