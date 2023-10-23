export const details = {
  id: "embed",
  aliases: ["embeds"],
  description: "Send an embedded message.",
  p: "util/embed",
};

export const handler = ({ args }) => ({
  body: {
    embeds: args.map((a) => JSON.parse(a)),
  },
});
