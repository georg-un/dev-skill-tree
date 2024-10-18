import { useRegisterEvents } from "@react-sigma/core";
import { FC, useEffect } from "react";

export interface GraphEventsProps {
  onNodeClick: (nodeId: string) => void;
  onStageClick: () => void;
}

export const GraphEvents: FC<GraphEventsProps> = ({ onNodeClick, onStageClick }) => {
  const registerEvents = useRegisterEvents();

  useEffect(() => {
    registerEvents({
      clickNode: (event) => onNodeClick(event.node),
      clickStage: onStageClick,
    });
  }, [registerEvents]);

  return null;
};
