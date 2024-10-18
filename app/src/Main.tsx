import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import { GraphEvents } from "./GraphEvents.tsx";
import { NodeModal } from "./NodeModal.tsx";
import { Settings } from "sigma/settings";
import { hoverRenderer } from "./hover-renderer.ts";
import { useEffect, useMemo, useState } from "react";
import { useTheme } from "./useTheme.ts";
import { useGraphData } from "./useGraphData.ts";
import Graph from "graphology";

const LoadGraph = ({ graphData }: { graphData: object }) => {
  const loadGraph = useLoadGraph();
  const graph = new Graph();

  useEffect(() => {
    if (graphData) {
      graph.import(graphData, true);
      loadGraph(graph);
    }
  }, [loadGraph, graphData]);

  return null;
}

export const Main = () => {
  const theme = useTheme();
  const { graphData, setSkill } = useGraphData({
    nodeEmptyColor: theme.primary,
    nodeFilledColor: theme.isDarkMode ? '#FFFFFF' : '#000000'
  });
  const [currentNodeId, setCurrentNodeId] = useState<string | null>(null);

  const sigmaSettings: Partial<Settings> = {
    defaultNodeColor: theme.primary,
    defaultEdgeColor: theme.secondary,
    labelColor: { color: theme.text },
    hoverRenderer: hoverRenderer,
  };

  const currentNode = useMemo(() => {
    return graphData?.nodes!.filter((node) => node.key === currentNodeId)?.[0];
  }, [graphData?.nodes, currentNodeId]);

  const handleSkillLevelChange = (nodeId: string, skillLevel: number) => {
    setSkill(nodeId, skillLevel);
  }

  const handleModalClose = () => {
    setCurrentNodeId(null);
  }

  return (
    <div style={{ display: "flex" }}>
      <SigmaContainer style={{ height: "100vh", width: "70vw", backgroundColor: theme.background }}
                      settings={sigmaSettings}>
        <LoadGraph graphData={graphData}/>
        <GraphEvents onNodeClick={setCurrentNodeId}/>
      </SigmaContainer>
      <div style={{ backgroundColor: theme.secondary, color: theme.text, width: '30vw' }}>
        {!!currentNode && <NodeModal node={currentNode} onClose={handleModalClose}
                                     onSkillLevelChange={(skillLevel) => handleSkillLevelChange(currentNode.key, skillLevel)}/>}
      </div>
    </div>
  );
}
