import { ChangeEvent, FC } from "react";
import { GraphNode } from "./types.ts";

export interface NodeModalProps {
  node: GraphNode,
  onClose: () => void,
  onSkillLevelChange: (skillLevel: number) => void;
}

export const NodeModal: FC<NodeModalProps> = ({ node, onClose, onSkillLevelChange }) => {
  const skillLevel = node.attributes['skillLevel'] ?? 0;

  const handleSkillLevelChange = (event: ChangeEvent<HTMLInputElement>) => {
    onSkillLevelChange(Number(event.target.value));
  }

  return (
    <div className="modal">
      <h2>Node Details</h2>
      <pre>{JSON.stringify(node, null, 2)}</pre>
      <input type="range" min="0" max="1" step="0.1" value={skillLevel} onChange={handleSkillLevelChange} />
      <button onClick={onClose}>Close</button>
    </div>
  );
}
