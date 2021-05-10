export let keywords = {}
import { FridayAPI } from "../FridayAPI";

export let initKeywords = () => {
  // does GC of unused recordings.. not most elegant solution
  // but will do for now.
  return FridayAPI.recordingClips().then(recordings => {
    FridayAPI.getExamples().then(examples => {

      let recordingsToRemove = recordings.ids;
      for (var [file, keyword] of Object.entries(examples)) {
        if (!(keyword in keywords)) {
          keywords[keyword] = [];
        }

        keywords[keyword].push(file);

        recordingsToRemove = recordingsToRemove.filter(item => item != file);
      }

      recordingsToRemove.forEach(clip => FridayAPI.recordingRemove(clip));

      return "ok"
    });
  });
}

export let keywordSync = () => {
  let examples = { }

  for (var [keyword, files] of Object.entries(keywords)) {
    files.forEach(file => {
      examples[file] = keyword;
    });
  }

  return FridayAPI.setExamples(examples);
}
