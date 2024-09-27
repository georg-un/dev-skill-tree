import { random } from "graphology-layout";

/**
 * Pseudo Random Generator that allows setting a seed.
 * Copied from https://stackoverflow.com/a/47593316/9291522
 */
function Mulberry32PRG(seed: number) {
  return function () {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
}


export const assignRandomLayout = (graph) => {
  const rng = Mulberry32PRG(42);
  random.assign(graph, { rng });
}
