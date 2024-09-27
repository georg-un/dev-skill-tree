import { writeFileSync } from "fs";

export const storeResult = (graph) => {
  const data = JSON.stringify(graph.toJSON());
  writeFileSync('../app/src/assets/graph.json', data);
}
