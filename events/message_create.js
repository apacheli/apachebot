import { parse } from "@apacheli/std/lib/args_parser.js";

export default "MESSAGE_CREATE";

export const handler = async (bot, message) => {
  if (message.author.bot || message.content.substring(0, bot.prefix.length) !== bot.prefix) {
    return;
  }
  const { args, kwargs } = parse(message.content.substring(bot.prefix.length));
  const commandName = args.shift().toLowerCase();
  const command = bot.commands.get(commandName) || bot.commands.get(bot.aliases.get(commandName));
  if (command === undefined) {
    return;
  }
  try {
    const response = await command.handler({ args, bot, commandName, kwargs, message });
    if (response === undefined) {
      return;
    }
    await bot.rest.createMessage(message.channel_id, typeof response === "object" ? response : { body: { content: response } });
  } catch (error) {
    await bot.rest.createMessage(message.channel_id, {
      body: {
        content: `An error occurred: \`${error.name}: ${error.message}\``,
      },
    });
  }
};
