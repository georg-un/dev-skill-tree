import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css"
import Graph from "graphology";

import SerializedGraph from './assets/graph.json';
import { NodeModal } from "./NodeModal.tsx";
import { GraphEvents } from "./GraphEvents.tsx";
import { Settings } from "sigma/settings";
import { hoverRenderer } from "./hover-renderer.ts";
import { useTheme } from "./useTheme.ts";

const LoadGraph = () => {
  const loadGraph = useLoadGraph();

  useEffect(() => {
    const graph = new Graph();
    graph.import(SerializedGraph);

    loadGraph(graph);
  }, [loadGraph]);

  return null;
}

function App() {
  const theme = useTheme();
  const [currentNodeId, setCurrentNodeId] = useState<string | null>(null);

  const sigmaSettings: Partial<Settings> = {
    defaultNodeColor: theme.primary,
    defaultEdgeColor: theme.secondary,
    labelColor: { color: theme.text },
    hoverRenderer: hoverRenderer,
  };

  const currentNode = useMemo(() => {
    return SerializedGraph.nodes.filter((node) => node.key === currentNodeId)?.[0];
  }, [SerializedGraph.nodes, currentNodeId]);

  const handleModalClose = () => {
    setCurrentNodeId(null);
  }

  return (
    <div style={{ display: "flex" }}>
      <SigmaContainer style={{ height: "100vh", width: "70vw", backgroundColor: theme.background }} settings={sigmaSettings}>
        <LoadGraph/>
        <GraphEvents onNodeClick={setCurrentNodeId} />
      </SigmaContainer>
      <div style={{ backgroundColor: theme.secondary, color: theme.text, width: '30vw' }}>
        {!!currentNode && <NodeModal node={currentNode} onClose={handleModalClose}/>}
      </div>
    </div>
  )
}

export default App
