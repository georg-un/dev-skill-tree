import forceAtlas2, { ForceAtlas2Settings } from "graphology-layout-forceatlas2";
import Graph from "graphology";

export const FORCE_ATLAS_2_SETTINGS_FIRST_ITERATION: ForceAtlas2Settings = {
  adjustSizes: false,
  barnesHutOptimize: false,
  barnesHutTheta: 1.2,
  edgeWeightInfluence: 0.05,
  gravity: 0.005,
  linLogMode: true,
  outboundAttractionDistribution: false,
  scalingRatio: 1.0,
  slowDown: 1000,
  strongGravityMode: false,
};

export const FORCE_ATLAS_2_SETTINGS_SECOND_ITERATION: ForceAtlas2Settings = {
  adjustSizes: true,
  barnesHutOptimize: false,
  barnesHutTheta: 1.2,
  edgeWeightInfluence: 1.0,
  gravity: 0.05,
  linLogMode: true,
  outboundAttractionDistribution: false,
  scalingRatio: 1.0,
  slowDown: 1,
  strongGravityMode: false,
};

export const runForceAtlas2 = (graph: Graph) => {
  forceAtlas2.assign(graph, {
    settings: FORCE_ATLAS_2_SETTINGS_FIRST_ITERATION,
    iterations: 50_000,
    getEdgeWeight: 'weight'
  });
  forceAtlas2.assign(graph, {
    settings: FORCE_ATLAS_2_SETTINGS_SECOND_ITERATION,
    iterations: 5000,
    getEdgeWeight: 'weight'
  });
}
