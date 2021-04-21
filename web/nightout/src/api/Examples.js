// This will be could possibly be called a lot 
// nice to cache the results
let examplesCache = null;
export async function APIGetExamples(prefix) {
    if (examplesCache == null) {
        examplesCache = await fetch(
                prefix + "/friday-inference/tensorflow-models/ddl/examples")
            .then(r => r.json())
    }
    return examplesCache;
}

export function APIClearExamplesCache() {
  examplesCache = null;
}

export async function APISetExamples(prefix, data) {
    return fetch(
            prefix + "/friday-inference/tensorflow-models/ddl/examples", {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "PUT",
                body: data
            }
        );
}
