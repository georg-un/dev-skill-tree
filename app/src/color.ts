type RGB = [number, number, number];

const rgbToHex = (color: RGB) => '#' + color.map(x => {
  const hex = x.toString(16)
  return hex.length === 1 ? '0' + hex : hex
}).join('')

const hexToRgb = hex =>
  hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i
    ,(m, r, g, b) => '#' + r + r + g + g + b + b)
    .substring(1).match(/.{2}/g)
    .map(x => parseInt(x, 16))

export const interpolateColor = (color1: string, color2: string, factor: number): string => {
  const color1Rgb = hexToRgb(color1);
  const color2Rgb = hexToRgb(color2);
  const r = Math.round(color1Rgb[0] + factor * (color2Rgb[0] - color1Rgb[0]));
  const g = Math.round(color1Rgb[1] + factor * (color2Rgb[1] - color1Rgb[1]));
  const b = Math.round(color1Rgb[2] + factor * (color2Rgb[2] - color1Rgb[2]));

  return rgbToHex([r, g, b]);
}
