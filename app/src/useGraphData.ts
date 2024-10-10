import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import SerializedGraph from "./assets/graph.json";
import { SKILLS_MOCK } from "../public/skills-mock.ts";
import { useMemo } from "react";

const SKILLS_QUERY_KEY = 'skills';

const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => Promise.resolve(SerializedGraph),
    staleTime: Infinity,
  });
}

const useSkills = () => {
  return useQuery({
    queryKey: [SKILLS_QUERY_KEY],
    queryFn: async () => {
      const stored = localStorage.getItem(SKILLS_QUERY_KEY);
      if (stored) return JSON.parse(stored);
      localStorage.setItem(SKILLS_QUERY_KEY, JSON.stringify(SKILLS_MOCK));
      return SKILLS_MOCK;
    },
  });
}

const useUpdateSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ nodeId, value }) => {
      const skills = queryClient.getQueryData([SKILLS_QUERY_KEY]);
      const updatedSkills = {
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

export const useGraphData = () => {
  const categoriesQuery = useCategories();
  const skillsQuery = useSkills();
  const updateSkillMutation = useUpdateSkill();

  const graphData = useMemo(() => {
    if (!categoriesQuery.data || !skillsQuery.data) return null;
    return {
      nodes: categoriesQuery.data.nodes.map(node => ({
        ...node,
        attributes: {
          ...node.attributes,
          skillLevel: skillsQuery.data[node.key],
        }
      })),
      edges: categoriesQuery.data.edges
    };
  }, [categoriesQuery.data, skillsQuery.data]);

  return {
    graphData,
    setSkill: (nodeId, value) => updateSkillMutation.mutate({ nodeId, value }),
    refetchSkills: () => skillsQuery.refetch(),
    isLoading: categoriesQuery.isLoading || skillsQuery.isLoading,
    isError: categoriesQuery.isError || skillsQuery.isError || updateSkillMutation.isError
  };
}
