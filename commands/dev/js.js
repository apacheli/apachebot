const inspectOptions = { depth: 0, colors: true };

export const details = {
  id: "js",
  aliases: ["code", "eval", "javascript", "ts", "typescript"],
  description: "Evaluate JavaScript code.",
  p: "dev/js",
  flags: {
    silent: "print to the terminal",
  },
};

export const handler = async ({ message, args, kwargs }) => {
  if (message.author.id !== "460612586061430806") {
    return;
  }
  let result;
  try {
    result = await eval(args[0]);
  } catch (e) {
    result = e;
  }
  if (kwargs.silent) {
    console.log(result);
    return;
  }
  return {
    files: [
      new File([Deno.inspect(result, inspectOptions)], `${Date.now()}.ansi`),
    ],
  };
};
