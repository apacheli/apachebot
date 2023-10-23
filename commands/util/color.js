import { rgb, rgbToCmyk, rgbToHls, rgbToHsv } from "@apacheli/std/lib/color.js";
import { field } from "../../util/embed.js";

export const details = {
  id: "color",
  aliases: ["colour", "hex", "hsb", "hls", "hsl", "hsv", "rgb"],
  description: "Display multiple color formats.",
  p: "util/color",
};

const { abs, floor } = Math;

export const handler = ({ args }) => {
  let color = args[0] ?? floor(Math.random() * 16777215);
  if (typeof color === "string") {
    if (color[0] !== "#") {
      return "Bad color.";
    }
    color = parseInt(color.substring(1), 16);
  }
  if (Number.isNaN(color) || color < 0 || color > 16777215) {
    return "Bad color.";
  }
  const [r, g, b] = rgb(color);
  const rc = r / 255;
  const gc = g / 255;
  const bc = b / 255;
  const [h, l, s] = rgbToHls(rc, gc, bc);
  const [h1, s1, v] = rgbToHsv(rc, gc, bc);
  const [c, m, y, k] = rgbToCmyk(rc, gc, bc);
  const embed = {
    title: closestColor(r, g, b),
    color,
    fields: [
      field("Decimal", color),
      field("Hexadecimal", `#${color.toString(16).padStart(6, "0")}`),
      field("RGB", `${r}, ${g}, ${b}`),
      field("HLS", `${floor(h * 360)}\u00B0, ${floor(l * 100)}%, ${floor(s * 100)}%`),
      field("HSV", `${floor(h1 * 360)}\u00B0, ${floor(s1 * 100)}%, ${floor(v * 100)}%`),
      field("CMYK", `${floor(c * 100)}%, ${floor(m * 100)}%, ${floor(y * 100)}%, ${floor(k * 100)}%`),
    ],
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};

const colors = {
  "Black": [0, 0, 0],
  "White": [255, 255, 255],
  "Red": [255, 0, 0],
  "Orange": [255, 128, 0],
  "Yellow": [255, 255, 0],
  "Lime": [128, 255, 0],
  "Green": [0, 255, 0],
  "Aquamarine": [0, 255, 128],
  "Aqua": [0, 255, 255],
  "Azure": [0, 128, 255],
  "Blue": [0, 0, 255],
  "Purple": [128, 0, 255],
  "Magenta": [255, 0, 255],
  "Fuchsia": [255, 0, 128],
};

const closestColor = (r, g, b) => {
  let c, s = Infinity;
  for (const color in colors) {
    const [cr, cg, cb] = colors[color];
    const d = abs(r - cr) + abs(g - cg) + abs(b - cb);
    if (s > d) {
      s = d;
      c = color;
    }
  }
  return c;
};
