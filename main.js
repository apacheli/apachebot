import { CacheClient, closeOnInterrupt, GatewayClient, RestClient } from "whirlybird";
import { readDirRecursive } from "@apacheli/std/lib/fs.js";

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

(async () => {
  for await (const filePath of readDirRecursive("./commands")) {
    const command = await import(filePath);
    commands.set(command.details.id, command);
    for (const alias of command.details.aliases) {
      aliases.set(alias, command.details.id);
    }
  }
})();

(async () => {
  for await (const filePath of readDirRecursive("./events")) {
    const event = await import(filePath);
    events.set(event.default, event.handler);
  }
})();

const bot = {
  aliases,
  cache,
  commands,
  events,
  gateway,
  prefix: "===",
  rest,
};
