export const details = {
  id: "time",
  aliases: ["date", "timestamp"],
  description: "Display the time.",
  p: "util/time",
  flags: {
    format: "timestamp format",
  },
};

export const flags = {
  string: ["format"],
};

export const handler = ({ args }) => `<t:${Math.floor(new Date(args._[0] ?? Date.now()).getTime() / 1e+3)}:${args.format ?? "f"}>`;
