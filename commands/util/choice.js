import { choice } from "@apacheli/std/lib/random.js";

export const details = {
  id: "choice",
  aliases: ["choices", "choose", "gamble", "options", "pick"],
  description: "Make a choice for you.",
  p: "util/choice",
};

export const handler = ({ args }) => choice(args);
