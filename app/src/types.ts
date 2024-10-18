import { SerializedGraph, SerializedNode } from "graphology-types";


export type Skills = Record<string, number>;

export type SkillResources = {
  iconUrl?: string;
  description: string;
}

export type GraphNode = SerializedNode<{ skillLevel?: number, color: string, label: string }>;

export type Graph = { nodes: Array<GraphNode> } & SerializedGraph;
