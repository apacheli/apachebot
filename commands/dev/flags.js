export const details = {
  id: "flags",
  aliases: ["args", "parse"],
  description: "Parse your message into bash-like arguments.",
  p: "dev/flags",
};

export const handler = ({ args, input }) => `\`\`\`json\n${JSON.stringify(input, null, 2)}\n\`\`\`\n\`\`\`json\n${JSON.stringify(args, null, 2)}\n\`\`\``;
