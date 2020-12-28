// This will be called quite a lot I can imagine
// nice to cache the results
let hueLightsCache = null;
export async function APIGetHueLights(prefix) {
    if (hueLightsCache == null) {
        hueLightsCache = await fetch(
                prefix + "/friday-vendor/philips-hue/lights")
            .then(r => r.json());
    }
    return hueLightsCache;
}

export async function APISetHueLights(prefix, data) {
    return fetch(
        prefix + "/friday-vendor/philips-hue/lights", {
            headers: {
                "Content-Type": "application/json"
            },
            method: "PUT",
            body: data
        }
    );
}


export async function APIGetHueLightsCommands(prefix) {
    return fetch(
            prefix + "/friday-vendor/philips-hue/lights/commands")
        .then(r => {
            if (r.status == 200) {
                return r.json()
            } else {
                return {}
            }
        });
}

export async function APISetHueLightsCommands(prefix, data) {
    return fetch(
            prefix + "/friday-vendor/philips-hue/lights/commands", {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "PUT",
                body: data
            }
        );
}
