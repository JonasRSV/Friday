// This will be could possibly be called a lot 
// nice to cache the results
let keywordsCache = null;
export async function APIGetKeywords(prefix) {
    if (keywordsCache == null) {
        keywordsCache = await fetch(
                prefix + "/friday-inference/tensorflow-models/discriminative/classes")
            .then(r => r.json())
            .then(j => {
                // TODO: this should be done by the backend 
                return j.slice(1, j.length);
            });
    }
    return keywordsCache;
}
