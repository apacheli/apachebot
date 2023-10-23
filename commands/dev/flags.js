export const details = {
  id: "flags",
  aliases: ["args", "kwargs", "parse"],
  description: "Parse your message into bash-like arguments.",
  p: "dev/flags",
};

export const handler = ({ args, kwargs }) => `\`\`\`json\n${JSON.stringify({ args, kwargs }, null, 2)}\n\`\`\``;
