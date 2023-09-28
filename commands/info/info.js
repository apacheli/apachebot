export const details = {
  id: "info",
  aliases: ["bot", "information", "memory", "stats", "statistics"],
  description: "Show information about the bot.",
  p: "info/info",
};

export const handler = () => {
  const embed = {
    title: "Info about apachebot",
    fields: [
      {
        name: "Source",
        value: "https://github.com/apacheli/apachebot",
      },
      {
        name: "apachebot",
        value: "1.0.0",
        inline: true,
      },
      {
        name: "whirlybird",
        value: "0.0.1",
        inline: true,
      },
      {
        name: "Deno",
        value: Deno.version.deno,
        inline: true,
      },
      {
        name: "Memory Usage",
        value: `${(Deno.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB`,
        inline: true,
      },
    ],
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};
