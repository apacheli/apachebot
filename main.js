import { CacheClient, closeOnInterrupt, GatewayClient, RestClient } from "whirlybird";

const token = `Bot ${Deno.env.get("BOT_TOKEN")}`;

const cache = new CacheClient();
const rest = new RestClient(token);

const handleEvent = (event, data, shard) => {
  cache.handleEvent(event, data);
  events.get(event)?.(bot, data, shard);
};

const gateway = new GatewayClient({
  handleEvent,
  identifyOptions: {
    intents: 1 << 9 | 1 << 15,
    presence: {
      activities: [{ name: "running on whirlybird", type: 0 }],
    },
  },
  token,
  url: "wss://gateway.discord.gg",
});

gateway.connect();

closeOnInterrupt(gateway);

const aliases = new Map();
const commands = new Map();
const events = new Map();

const importAll = async (path) => {
  const mods = [];
  for await (const dirEntry of Deno.readDir(path)) {
    const filePath = `${path}/${dirEntry.name}`;
    mods.push(dirEntry.isDirectory ? importAll(filePath) : import(filePath));
  }
  return (await Promise.all(mods)).flat();
};

for (const command of await importAll("./commands")) {
  commands.set(command.details.id, command);
  for (const alias of command.details.aliases) {
    aliases.set(alias, command.details.id);
  }
}

for (const event of await importAll("./events")) {
  events.set(event.default, event.handler);
}

const bot = {
  aliases,
  cache,
  commands,
  events,
  gateway,
  prefix: "===",
  rest,
};
