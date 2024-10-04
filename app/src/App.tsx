import { useEffect } from 'react'
import './App.css'
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css"
import Graph from "graphology";

import SerializedGraph from './assets/graph.json';
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

  const sigmaSettings: Partial<Settings> = {
    defaultNodeColor: theme.primary,
    defaultEdgeColor: theme.secondary,
    labelColor: { color: theme.text },
    hoverRenderer: hoverRenderer,
  };

  return (
    <div>
      <SigmaContainer style={{ height: "100vh", width: "100vw" }}>
    <div style={{ display: "flex" }}>
      <SigmaContainer style={{ height: "100vh", width: "70vw", backgroundColor: theme.background }} settings={sigmaSettings}>
        <LoadGraph/>
      </SigmaContainer>
    </div>
  )
}

export default App
