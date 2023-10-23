export const details = {
  id: "time",
  aliases: ["date", "timestamp"],
  description: "Display the time.",
  p: "util/time",
  flags: {
    format: "timestamp format",
  },
};

export const handler = ({ args, kwargs }) => {
  return `<t:${Math.floor((args[0] ? new Date(args[0]).getTime() : Date.now()) / 1e+3)}:${kwargs.format ?? "f"}>`;
};
