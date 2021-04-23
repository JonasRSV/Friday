function makeid(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

export class Command {
    static New() {
        return new Command("Mr", []);
    }

    constructor(keyword, scripts) {
        // ID is for svelte 
        this.id = makeid(10);

        // Reference to component that renders this action
        this.component = null;

        this.keyword = keyword;
        this.scripts = scripts;
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

    setScripts(scripts) {
        if (this.component != null) {
            // The component will set the value 
            // of this and also update the UI
            this.component.setScripts(scripts)
        } else {
            this.scripts = scripts
        }
    }
}
