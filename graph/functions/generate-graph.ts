import Graph from "graphology";

export interface Tag {
  tag: string;
  count: number;
  cluster: number;
}

export interface Score {
  tag1: string;
  tag2: string;
  pairCount: number;
  pairCountNormalized: number;
}

export const generateGraph = (tags: Tag[], scores: Score[]) => {
  const graph = new Graph();

  const countMax = Math.max(...tags.map((tag) => tag.count));
  const pairCountNormalizedMax = scores.map((scorePair) => scorePair.pairCountNormalized)
    .reduce((acc, curr) => Math.max(acc, curr), 0);
  const pairCountMax = scores.map((scorePair) => scorePair.pairCount)
    .reduce((acc, curr) => Math.max(acc, curr), 0);

  tags.forEach((tag) => {
    const nodeSize = Math.sqrt((tag.count / countMax)) * 30;
    graph.addNode(tag.tag, { size: nodeSize, label: tag.tag });
  });

  scores.forEach((scorePair) => {
    const { tag1: source, tag2: target, pairCount, pairCountNormalized, ...attributes } = scorePair;
    if (source === 'constructor' || target === 'constructor') {
      // 'constructor' is a tag name and if we set it, it breaks the graph object :)
      return;
    }

    const weight = (pairCountNormalized / pairCountNormalizedMax);
    if (weight > 0.01) {
      graph.addEdge(source, target, { ...attributes, weight });
    }
  });

  return graph;
}
