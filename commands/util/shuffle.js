import { shuffle } from "@apacheli/std/lib/random.js";

export const details = {
  id: "shuffle",
  aliases: [],
  description: "Shuffle a list.",
  p: "util/shuffle",
};

export const handler = ({ args }) => `\`\`\`json\n${JSON.stringify(shuffle(args), null, 2)}\n\`\`\``;
