import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import SerializedGraph from "./assets/graph.json";
import { SKILLS_MOCK } from "../public/skills-mock.ts";
import { useMemo } from "react";
import { Graph, GraphNode, Skills } from "./types.ts";
import { interpolateColor } from "./color.ts";

const SKILLS_QUERY_KEY = 'skills';

const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => Promise.resolve(SerializedGraph as Graph),
    staleTime: Infinity,
  });
}

const useSkills = () => {
  return useQuery({
    queryKey: [SKILLS_QUERY_KEY],
    queryFn: async () => {
      const stored = localStorage.getItem(SKILLS_QUERY_KEY);
      if (stored) return JSON.parse(stored) as Skills;
      localStorage.setItem(SKILLS_QUERY_KEY, JSON.stringify(SKILLS_MOCK));
      return SKILLS_MOCK;
    },
  });
}

const useUpdateSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ nodeId, value }) => {
      const skills: Skills | undefined = queryClient.getQueryData([SKILLS_QUERY_KEY]);
      const updatedSkills: Skills = {
        ...skills,
        [nodeId]: value
      };
      localStorage.setItem(SKILLS_QUERY_KEY, JSON.stringify(updatedSkills));
      return Promise.resolve(updatedSkills);
    },
    onSuccess: (updatedSkills) => {
      queryClient.setQueryData([SKILLS_QUERY_KEY], updatedSkills);
    },
  });
}

export interface UseGraphDataProps {
  nodeEmptyColor: string;
  nodeFilledColor: string;
}

export const useGraphData = ({ nodeEmptyColor, nodeFilledColor }: UseGraphDataProps) => {
  const categoriesQuery = useCategories();
  const skillsQuery = useSkills();
  const updateSkillMutation = useUpdateSkill();

  const addSkillLevel = (node: GraphNode, skills: Skills): GraphNode => {
    return {
      ...node,
      attributes: {
        ...node.attributes,
        skillLevel: skills[node.key],
      },
    };
  };

  const addColor  = (node: GraphNode, colorEmpty: string, colorFilled: string): GraphNode => {
    return {
      ...node,
      attributes: {
        ...node.attributes,
        color: interpolateColor(colorEmpty, colorFilled, node.attributes.skillLevel ?? 0),
      }
    }
  }

  const graphData = useMemo(() => {
    if (!categoriesQuery.data || !skillsQuery.data) return null;
    return {
      nodes: categoriesQuery.data.nodes
        .map((node) => addSkillLevel(node, skillsQuery.data))
        .map((node) => addColor(node, nodeEmptyColor, nodeFilledColor)),
      edges: categoriesQuery.data.edges
    };
  }, [categoriesQuery.data, skillsQuery.data, nodeEmptyColor, nodeFilledColor]);

  return {
    graphData,
    setSkill: (nodeId, value) => updateSkillMutation.mutate({ nodeId, value }),
    refetchSkills: () => skillsQuery.refetch(),
    isLoading: categoriesQuery.isLoading || skillsQuery.isLoading,
    isError: categoriesQuery.isError || skillsQuery.isError || updateSkillMutation.isError
  };
}
