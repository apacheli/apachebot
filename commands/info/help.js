export const details = {
  id: "help",
  aliases: ["?", "command", "commands"],
  description: "Display a list of commands.",
  p: "info/help",
  flags: {
    text: "display in text format",
  },
};

export const flags = {
  boolean: ["text"],
};

export const handler = ({ bot, args }) => {
  const commandName = args._[0];
  if (!commandName) {
    if (args.text) {
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
  const command = bot.commands.get(bot.aliases.get(commandName) ?? commandName);
  if (!command) {
    return `\`${commandName}\` command not found. Type \`${bot.prefix}help\` for a list of commands.`;
  }
  const { flags, details } = command;
  let usage = "";
  let opts = "";
  if (flags?.boolean) {
    for (const bool of flags.boolean) {
      usage += ` [--${bool}]`;
      opts += `\n${args.text ? `  --${bool}        ` : `\`--${bool}\`: `}${details.flags[bool]}`;
    }
  }
  if (flags?.string) {
    for (const str of flags.string) {
      usage += ` [--${str}]`;
      opts += `\n${args.text ? `  --${str} [str]        ` : `\`--${str} [str]\`: `}${details.flags[str]}`;
    }
  }
  const source = `https://github.com/apacheli/apachebot/tree/master/commands/${details.p}.js`;
  if (args.text) {
    let str = `\`\`\`\n${bot.prefix}${details.id} [...]${usage}\n\n${details.description}\n\nSource: ${source}\n`;
    if (opts.length > 0) {
      str += `\nOptions:${opts}\n`;
    }
    str += "```";
    return str;
  }
  const fields = [
    { name: "Source", value: source },
  ];
  if (opts.length > 0) {
    fields.push({ name: "options", value: opts.slice(1) });
  }
  const embed = {
    title: details.id,
    description: `\`${bot.prefix}${details.id} [...]${usage}\`\n\n${details.description}`,
    fields,
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};
