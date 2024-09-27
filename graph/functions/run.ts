import { generateGraph } from "./generate-graph.ts";
import { assignRandomLayout } from "./layout-random.ts";
import { runForceAtlas2 } from "./layout-force-atlas-2.ts";
import { storeResult } from "./store-result.ts";

import Tags from '../../data/result/tags.json';
import Scores from '../../data/result/tag-pairs.json';

const main = () => {
  // noinspection TypeScriptValidateTypes
  const graph = generateGraph(Tags, Scores);
  assignRandomLayout(graph);
  runForceAtlas2(graph);
  storeResult(graph);
}

main();
