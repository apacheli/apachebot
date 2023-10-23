export const details = {
  id: "shards",
  aliases: ["gateway", "gw", "heartbeat", "latency", "shard"],
  description: "Show shard latency.",
  p: "dev/shards",
};

export const handler = ({ bot }) => {
  const fields = [];
  let i = 0;
  for (const shard of bot.gateway.shards.values()) {
    fields.push({
      name: `Shard ${i++}`,
      value: `${shard.latency} ms`,
    });
  }
  const embed = {
    title: "Shards",
    fields,
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};
