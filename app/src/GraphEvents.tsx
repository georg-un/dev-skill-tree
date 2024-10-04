import { useRegisterEvents } from "@react-sigma/core";
import { FC, useEffect } from "react";

export interface GraphEventsProps {
  onNodeClick: (nodeId: string) => void;
}

export const GraphEvents: FC<GraphEventsProps> = ({ onNodeClick }) => {
  const registerEvents = useRegisterEvents();

  useEffect(() => {
    registerEvents({
      clickNode: (event) => onNodeClick(event.node),
    });
  }, [registerEvents]);

  return null;
};
