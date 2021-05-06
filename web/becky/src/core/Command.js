

export let commands = {};

export let initCommands = () => {
  return new Promise((resolve, _) => {
    setTimeout(() => {
      commands = {
        "hello": ["what.py", "who.py"],
        "when": ["where.sh", "cool.sh"]
      }
      resolve(commands);
    }, 1000);
  });
}

export let setCommands = (c) => commands = c;

