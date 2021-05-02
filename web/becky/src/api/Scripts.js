// This will be called quite a lot I can imagine
// nice to cache the results
let boundScriptsCache = null;
export async function APIGetBoundScripts(prefix) {
    if (boundScriptsCache == null) {
        boundScriptsCache = await fetch(
                prefix + "/friday-vendor/scripts/bound")
            .then(r => r.json());
    }
    return boundScriptsCache;
}

export function APIClearBoundScriptsCache() {
  boundScriptsCache = null;
}

export async function APISetBoundScripts(prefix, data) {
    return fetch(
        prefix + "/friday-vendor/scripts/bound", {
            headers: {
                "Content-Type": "application/json"
            },
            method: "PUT",
            body: data
        }
    );
}

let allScriptsCache = null
export async function APIGetAllScripts(prefix) {
    if (allScriptsCache == null) {
        allScriptsCache = await fetch(
                prefix + "/friday-vendor/scripts/all")
            .then(r => r.json());
    }
    return allScriptsCache;
}
