import { FC } from "react";
import { NodeEntry } from "graphology-types";

export interface NodeModalProps {
  node: NodeEntry,
  onClose: () => void,
}

export const NodeModal: FC<NodeModalProps> = ({ node, onClose }) => {
  return (
    <div className="modal">
      <h2>Node Details</h2>
      <pre>{JSON.stringify(node, null, 2)}</pre>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
