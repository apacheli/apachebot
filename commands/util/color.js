export const details = {
  id: "color",
  aliases: ["colour", "hex", "hsb", "hls", "hsl", "hsv", "rgb"],
  description: "Display multiple color formats.",
  p: "util/color",
};

const { abs, floor, max, min, sqrt } = Math;

export const handler = ({ args }) => {
  const i = args._[0] ?? Math.floor(Math.random() * 16777215);
  const color = i[0] === "#" ? parseInt(i.substring(1), 16) : parseInt(i);
  if (color !== color || color < 0 || color > 16777215) {
    return "Bad color.";
  }
  const [r, g, b] = toRgb(color);
  const [h, l, s] = rgbToHls(r, g, b);
  const [h1, s2, v] = rgbToHsv(r, g, b);
  const [c, m, y, k] = rgbToCmyk(r, g, b);
  const field = (name, value) => ({ name, value, inline: true });
  const embed = {
    title: closestColor(r, g, b),
    color,
    fields: [
      field("Decimal", color),
      field("Hexadecimal", `#${color.toString(16).padStart(6, "0")}`),
      field("RGB", `${r}, ${g}, ${b}`),
      field("HLS", `${floor(h * 360)}\u00B0, ${floor(l * 100)}%, ${floor(s * 100)}%`),
      field("HSV", `${floor(h1 * 360)}\u00B0, ${floor(s2 * 100)}%, ${floor(v * 100)}%`),
      field("CMYK", `${floor(c)}%, ${floor(m)}%, ${floor(y)}%, ${floor(k * 100)}%`),
    ],
  };
  return {
    body: {
      embeds: [embed],
    },
  };
};

const toRgb = (d) => [d >> 16 & 255, d >> 8 & 255, d & 255];

// https://github.com/python/cpython/blob/3.11/Lib/colorsys.py#L125
const rgbToHsv = (r, g, b) => {
  const maxc = max(r, g, b);
  const minc = min(r, g, b);
  const v = maxc / 255;
  if (minc === maxc) {
    return [0, 0, v];
  }
  const d = maxc - minc;
  const s = d / maxc;
  const rc = (maxc - r) / d;
  const gc = (maxc - g) / d;
  const bc = (maxc - b) / d;
  let h;
  if (r == maxc) {
    h = bc - gc + (g < b ? 6 : 0);
  } else if (g == maxc) {
    h = 2 + rc - bc;
  } else {
    h = 4 + gc - rc;
  }
  h /= 6;
  return [h, s, v];
};

// https://github.com/python/cpython/blob/3.11/Lib/colorsys.py#L75
const rgbToHls = (r, g, b) => {
  const maxc = max(r, g, b);
  const minc = min(r, g, b);
  const c = maxc + minc;
  const l = c / 2 / 255;
  if (maxc === minc) {
    return [0, l, 0];
  }
  const d = maxc - minc;
  const s = d === 0 ? 0 : d / (1 - abs(2 * l - 1)) / 255;
  const rc = (maxc - r) / d;
  const gc = (maxc - g) / d;
  const bc = (maxc - b) / d;
  let h;
  if (r === maxc) {
    h = bc - gc + (g < b ? 6 : 0);
  } else if (g === maxc) {
    h = 2.0 + rc - bc;
  } else {
    h = 4.0 + gc - rc;
  }
  h /= 6;
  return [h, l, s];
};

const rgbToCmyk = (r, g, b) => {
  const k = max(r, g, b);
  const c = r && (k - r) / k * 100;
  const m = g && (k - g) / k * 100;
  const y = b && (k - b) / k * 100;
  return [c, m, y, k / -255 + 1];
};

const colors = {
  "Black": [0, 0, 0],
  "Gray": [128, 128, 128],
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
  "Hot Pink": [255, 0, 128],
};

const closestColor = (r, g, b) => {
  let c, s = Infinity;
  for (const color in colors) {
    const [cr, cg, cb] = colors[color];
    const d = sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2);
    if (s > d) {
      s = d;
      c = color;
    }
  }
  return c;
};
