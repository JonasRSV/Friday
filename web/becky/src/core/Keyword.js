export let keywords = {}

export let initKeywords = () => {
  return new Promise((resolve, _) => {
    setTimeout(() => {
      keywords = {
          "hello": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],

          "hi": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],
          "whats up": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],
          "lights on": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],
          "lights off": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],
          "cookie time": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ],
          "good night": [
            "123-222-333-111.wav",
            "223-222-333-111.wav",
            "223-333-333-111.wav",
          ]
      }

      resolve(keywords);
    }, 1000);
  });
}
