import Graph from "graphology";

export interface Tag {
  tag: string;
  count: number;
  cluster: number;
}

export interface Score {
  tag1: string;
  tag2: string;
  weight: number;
  pairCount: number;
  pairCountNormalized: number;
}

const WEIGHT_THRESHOLD = 0.01

export const generateGraph = (tags: Tag[], scores: Score[]) => {
  const graph = new Graph();

  const countMax = Math.max(...tags.map((tag) => tag.count));

  tags.forEach((tag) => {
    const nodeSize = Math.sqrt((tag.count / countMax)) * 30;
    graph.addNode(tag.tag, { size: nodeSize, label: tag.tag });
  });

  scores.forEach((scorePair) => {
    const { tag1: source, tag2: target, weight, ...attributes } = scorePair;
    if (source === 'constructor' || target === 'constructor') {
      // 'constructor' is a tag name and if we set it, it breaks the graph object :)
      return;
    }

    if (weight > WEIGHT_THRESHOLD) {
      graph.addEdge(source, target, { ...attributes, weight });
    }
  });

  return graph;
}
