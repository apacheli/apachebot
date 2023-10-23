import { rng } from "@apacheli/std/lib/random.js";

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

export const handler = ({ kwargs }) => rng(kwargs.max ?? 6, kwargs.min);
