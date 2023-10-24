export const details = {
  id: "shards",
  aliases: ["gateway", "gw", "heartbeat", "latency", "shard"],
  description: "Show shard latency.",
  p: "dev/shards",
};

export const handler = ({ bot }) => {
  let str = "";
  let i = 0;
  let average = 0;
  for (const shard of bot.gateway.shards.values()) {
    str += `Shard ${i++}: ${shard.latency} ms\n`;
    average += shard.latency;
  }
  return `\`\`\`\n${str}\nAverage: ${average / i} ms\`\`\``;
};
