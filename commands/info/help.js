export const details = {
  id: "help",
  aliases: ["?", "command", "commands"],
  description: "Display a list of commands.",
  p: "info/help",
  flags: {
    text: "display in text format",
  },
};

export const handler = ({ bot, args, kwargs }) => {
  const commandName = args[0];
  if (commandName === undefined) {
    if (kwargs.text) {
      const str = [...bot.commands.values()].map((c) => `${c.details.id}        ${c.details.description}`).join("\n");
      return `\`\`\`\nType \`${bot.prefix}help [...]\` for more details.\n\n${str}\n\`\`\``;
    }
    const embed = {
      title: "Commands",
      description: [...bot.commands.values()].map((c) => `\`${c.details.id}\``).join(", "),
      footer: {
        text: `Type \`${bot.prefix}help [...]\` for more details.`,
      },
    };
    return {
      body: {
        embeds: [embed],
      },
    };
  }
  const command = bot.commands.get(commandName) || bot.commands.get(bot.aliases.get(commandName));
  if (command === undefined) {
    return `\`${commandName}\` command not found. Type \`${bot.prefix}help\` for a list of commands.`;
  }
  const { details } = command;
  let usage = "";
  let flags = "";
  for (const flag in details.flags) {
    usage += ` [--${flag}]`;
    flags += `\n${kwargs.text ? `  --${flag}        ` : `\`--${flag}\`: `}${details.flags[flag]}`;
  }
  const source = `https://github.com/apacheli/apachebot/tree/master/commands/${details.p}.js`;
  if (kwargs.text) {
    let str = `\`\`\`\n${bot.prefix}${details.id} [...]${usage}\n\nSource: ${source}\n\n${details.description}\n`;
    if (flags.length > 0) {
      str += `\nOptions:${flags}\n`;
    }
    str += "```";
    return str;
  }
  const fields = [];
  if (flags.length > 0) {
    fields.push({ name: "options", value: flags.substring(1) });
  }
  const embed = {
    title: details.id,
    url: source,
    description: `\`${bot.prefix}${details.id} [...]${usage}\`\n\n${details.description}`,
    fields,
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};
