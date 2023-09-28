export const details = {
  id: "js",
  aliases: ["code", "eval", "javascript", "ts", "typescript"],
  description: "Evaluate JavaScript code.",
  p: "dev/js",
  flags: {
    silent: "print to the terminal",
  },
};

export const flags = {
  boolean: ["silent"],
};

export const handler = async ({ message, args }) => {
  if (message.author.id !== "460612586061430806") {
    return;
  }
  let result;
  try {
    result = await eval(args._[0]);
  } catch (e) {
    result = e;
  }
  if (args.silent) {
    console.log(result);
    return;
  }
  return {
    files: [
      new File([Deno.inspect(result, { depth: 0, colors: true })], `${Date.now()}.ansi`),
    ],
  };
};
