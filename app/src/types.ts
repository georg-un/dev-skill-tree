import { SerializedGraph, SerializedNode } from "graphology-types";


export type Skills = Record<string, number>;

export type GraphNode = SerializedNode<{ skillLevel?: number, color: string }>;

export type Graph = { nodes: Array<GraphNode> } & SerializedGraph;
