import { parse } from "https://deno.land/std@0.201.0/flags/mod.ts";

export default "MESSAGE_CREATE";

export const handler = async (bot, message) => {
  if (message.content.substring(0, bot.prefix.length) !== bot.prefix || message.author.bot) {
    return;
  }
  const matches = message.content.substring(bot.prefix.length).matchAll(/```(?:(?:.*?)\n+?)?([\s\S]*?)\n?```|(--.*?=)?(".*?"|'.*?'|`.*?`)|\S+/g);
  const commandName = matches.next().value[0].toLowerCase();
  const command = bot.commands.get(bot.aliases.get(commandName) ?? commandName);
  if (!command) {
    return;
  }
  const input = [...matches].map((x) => x[1] ?? (x[2] ?? "") + (x[3]?.slice(1, -1) ?? x[0]));
  const args = parse(input, command.flags);
  const content = await command.handler({ bot, message, args, commandName, input });
  if (content !== undefined) {
    await bot.rest.createMessage(message.channel_id, typeof content === "string" ? { body: { content } } : content);
  }
};
