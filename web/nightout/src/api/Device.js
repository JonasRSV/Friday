export async function APIGetDeviceName(prefix) {
    return fetch(
            prefix + "/friday-discovery/name")
        .then(r => r.json())
        .then(j => j.name);
}

export async function APISetDeviceName(prefix, data) {
    return fetch(
        prefix + "/friday-discovery/name", {
            headers: {
                "Content-Type": "application/json"
            },
            method: "PUT",
            body: data
        }
    )
}
