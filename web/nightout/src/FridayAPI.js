import {
    APIGetKeywords,
    APIClearKeywordsCache
} from "./api/Keywords.js";
import {
    APIGetExamples,
    APISetExamples,
    APIClearExamplesCache
} from "./api/Examples.js";
import {
    APIGetBoundScripts,
    APIClearBoundScriptsCache,
    APISetBoundScripts,
    APIGetAllScripts,
} from "./api/Scripts.js";

import {
    APIGetDeviceName,
    APISetDeviceName
} from "./api/Device";

import {
    APIRecordingNew,
    APIRecordingListen,
    APIRecordingGetClips,
    APIRecordingRemove,
    APIRecordingRename
} from "./api/Recording.js";

export class FridayAPI {
    // TODO: how to do this better?
    // For dev
    //static prefix = "http://" + window.location.host.slice(0, -5) + ":8000";
    // For production
    static prefix = "";

    static getDeviceName = () => APIGetDeviceName(this.prefix);
    static setDeviceName = (name) => APISetDeviceName(
        this.prefix,
        JSON.stringify({
            "name": name
        }));

    // Gets the DDL examples
    static getExamples = () => APIGetExamples(this.prefix);
    static setExamples = (examples) => {
      return APISetExamples(this.prefix, JSON.stringify(examples)).then(r => {
        // clear cache so next getExamples or getKeywords gets new
        APIClearExamplesCache();
        APIClearKeywordsCache();
      });
    }

    // Gets the keywords of the command e.g 'on' - 'off' etc
    static getKeywords = () => APIGetKeywords(this.prefix);

    static getBoundScripts = () => APIGetBoundScripts(this.prefix);
    static setBoundScripts = (scripts) => {
      return APISetBoundScripts(this.prefix, JSON.stringify(scripts)).then(r => {
        // clear cache so next getExamples or getKeywords gets new
        APIClearBoundScriptsCache();
      });
    }
    static getAllScripts = () => APIGetAllScripts(this.prefix);

    // Recording API
    static recordingNew = () => APIRecordingNew(this.prefix);
    static recordingRemove = (id) => APIRecordingRemove(
        this.prefix,
        {
            "id": id
        });
    static recordingRename = (oldId, newId) => APIRecordingRename(
        this.prefix,
        {
            "old_id": oldId,
            "new_id": newId
        });

    static recordingClips = () => APIRecordingGetClips(this.prefix);
    static recordingAudio = (id) => APIRecordingListen(
        this.prefix,
        {
            "id": id
        });

}
