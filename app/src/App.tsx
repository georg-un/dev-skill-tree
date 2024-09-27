import { useEffect } from 'react'
import './App.css'
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css"
import Graph from "graphology";

import SerializedGraph from './assets/graph.json';

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
  return (
    <div>
      <SigmaContainer style={{ height: "100vh", width: "100vw" }}>
        <LoadGraph/>
      </SigmaContainer>
    </div>
  )
}

export default App
