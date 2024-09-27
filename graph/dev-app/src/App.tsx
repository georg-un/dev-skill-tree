import { useEffect } from 'react'
import { ControlsContainer, SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css"
import { LayoutForceAtlas2Control } from "@react-sigma/layout-forceatlas2";
import { generateGraph } from "../../functions/generate-graph.ts";
import { assignRandomLayout } from "../../functions/layout-random";
import {
  FORCE_ATLAS_2_SETTINGS_FIRST_ITERATION,
  FORCE_ATLAS_2_SETTINGS_SECOND_ITERATION
} from "../../functions/layout-force-atlas-2";
import Tags from '../../../data/result/tags.json';
import Scores from '../../../data/result/tag-pairs.json';


const LoadGraph = () => {
  const loadGraph = useLoadGraph();

  useEffect(() => {
    // noinspection TypeScriptValidateTypes
    const graph = generateGraph(Tags, Scores);
    assignRandomLayout(graph);

    loadGraph(graph);
  }, [loadGraph]);

  return null;
}

function App() {

  return (
    <div>
      <SigmaContainer style={{ height: "100vh", width: "100vw" }} settings={{ allowInvalidContainer: true }}>
        <LoadGraph/>
        <ControlsContainer position={"bottom-left"}>
          <label>First iteration</label>
          <LayoutForceAtlas2Control settings={{ settings: FORCE_ATLAS_2_SETTINGS_FIRST_ITERATION }}/>
        </ControlsContainer>
        <ControlsContainer position={"bottom-right"}>
          <label>Second iteration</label>
          <LayoutForceAtlas2Control settings={{ settings: FORCE_ATLAS_2_SETTINGS_SECOND_ITERATION }}/>
        </ControlsContainer>
      </SigmaContainer>
    </div>
  )
}

export default App
