import { field } from "../../util/embed.js";

export const details = {
  id: "info",
  aliases: ["bot", "information", "memory", "stats", "statistics", "version"],
  description: "Show information about the bot.",
  p: "info/info",
};

export const handler = () => {
  const embed = {
    title: "Info about apachebot",
    url: "https://github.com/apacheli/apachebot",
    description: "Hello, I am apachebot. I was created by @apacheli.",
    fields: [
      field("apachebot", "1.0.0", true),
      field("whirlybird", "0.0.1", true),
      field("Deno", Deno.version.deno, true),
      field("Memory Usage", `${(Deno.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB`, true),
    ],
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};
