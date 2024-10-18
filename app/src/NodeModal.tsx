import './NodeModal.css';
import { FC } from "react";
import { GraphNode } from "./types.ts";
import { useSkillResources } from "./useSkillResources.ts";

export interface NodeModalProps {
  node: GraphNode,
  onClose: () => void,
  onSkillLevelChange: (skillLevel: number) => void;
}

export const NodeModal: FC<NodeModalProps> = ({ node, onClose, onSkillLevelChange }) => {
  const skillResourcesQuery = useSkillResources({ skill: node.key });

  let skillLevel = node.attributes['skillLevel'] ?? 0;
  skillLevel = Math.round(skillLevel / 0.25) * 0.25; // round to the nearest 0.25 step

  return (
    <div className="modal">
      <h2>{node.attributes.label}</h2>
      <span>{skillResourcesQuery.data?.description}</span>
      <fieldset>
        <legend>How proficient are you in {node.attributes.label}:</legend>

        <div>
          <input type="radio" id="proficiency-0" name="0%" value="0"
                 onChange={() => onSkillLevelChange(0)}
                 checked={skillLevel === 0}/>
          <label htmlFor="proficiency-0">0%</label>
        </div>

        <div>
          <input type="radio" id="proficiency-25" name="25%" value="0.25"
                 onChange={() => onSkillLevelChange(0.25)}
                 checked={skillLevel === 0.25}/>
          <label htmlFor="proficiency-25">25%</label>
        </div>

        <div>
          <input type="radio" id="proficiency-50" name="50%" value="0.5"
                 onChange={() => onSkillLevelChange(0.5)}
                 checked={skillLevel === 0.5}/>
          <label htmlFor="proficiency-50">50%</label>
        </div>

        <div>
          <input type="radio" id="proficiency-75" name="75%" value="0.75"
                 onChange={() => onSkillLevelChange(0.75)}
                 checked={skillLevel === 0.75}/>
          <label htmlFor="proficiency-75">75%</label>
        </div>

        <div>
          <input type="radio" id="proficiency-100" name="100%" value="1"
                 onChange={() => onSkillLevelChange(1)}
                 checked={skillLevel === 1}/>
          <label htmlFor="proficiency-100">100%</label>
        </div>
      </fieldset>


      <br/>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
