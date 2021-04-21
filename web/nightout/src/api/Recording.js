let clipsCache = null
export async function APIRecordingGetClips(prefix) {
    if (clipsCache == null) {
        clipsCache = await fetch(
                prefix + "/record/clips")
            .then(r => r.json())
            .then(j => {
                return j;
            });
    }
    return clipsCache;
}

export async function APIRecordingNew(prefix) {
    return await fetch(
            prefix + "/record/new")
        .then(r => r.json())
        .then(j => {
            if (clipsCache !== null) {
                clipsCache.ids.push(j.id)
            }
            return j;
        });
}

export async function APIRecordingListen(prefix, data) {
    return await fetch(
            prefix + "/record/listen", {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "POST",
                body: JSON.stringify(data)
            })
        .then(r => {
            return r;
        });
}

export async function APIRecordingRemove(prefix, data) {
    return await fetch(
            prefix + "/record/remove", {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "PUT",
                body: JSON.stringify(data)
            })
        .then(r => r.json())
        .then(j => {
            if (clipsCache !== null) {
                clipsCache.ids = clipsCache.ids.filter(v => v != data.id);
            }
            return j;
        });
}


export async function APIRecordingRename(prefix, data) {
    return await fetch(
            prefix + "/record/rename", {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "PUT",
                body: JSON.stringify(data)
            })
        .then(r => r.json())
        .then(j => {
            if (clipsCache !== null) {
                clipsCache.ids = clipsCache.ids.filter(v => v != data.oldId);
                clipsCache.ids.push(data.newId)
            }
            return j;
        });
}
