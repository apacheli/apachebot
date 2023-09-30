export const details = {
  id: "random",
  aliases: ["die", "dice", "number", "roll"],
  description: "Roll a random number.",
  p: "util/random",
  flags: {
    max: "maximum number",
    min: "minimum number",
  },
};

export const flags = {
  string: ["max", "min"],
};

export const handler = ({ args }) => {
  const max = parseInt(args.max ?? 6);
  const min = parseInt(args.min ?? 0);
  return `${min + Math.round(Math.random() * (max - min))}`;
};
