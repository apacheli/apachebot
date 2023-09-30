export const details = {
  id: "embed",
  aliases: ["embeds"],
  description: "Send an embedded message.",
  p: "util/embed",
};

export const handler = ({ args }) => {
  try {
    return {
      body: {
        embeds: args._.map((a) => JSON.parse(a)),
      },
    };
  } catch (error) {
    return `\`${error.message}\``;
  }
};
