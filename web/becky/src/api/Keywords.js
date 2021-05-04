//https://stackoverflow.com/questions/1960473/get-all-unique-values-in-a-javascript-array-remove-duplicates
function onlyUnique(value, index, self) {
  return self.indexOf(value) === index;
}
// This will be could possibly be called a lot 
// nice to cache the results
let keywordsCache = null;
export async function APIGetKeywords(prefix) {
    if (keywordsCache == null) {
        keywordsCache = await fetch(
                prefix + "/friday-inference/tensorflow-models/ddl/examples")
            .then(r => r.json())
            .then(j => {
                return Object.values(j).filter(onlyUnique)
            });
    }
    return keywordsCache;
}

export function APIClearKeywordsCache() {
  keywordsCache = null;
}
