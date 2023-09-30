export const details = {
  id: "pick",
  aliases: ["choice", "choices", "choose", "gamble", "options"],
  description: "if you are unable to think for yourself.",
  p: "util/pick",
};

export const handler = ({ args }) => args._[Math.floor(Math.random() * args._.length)];
