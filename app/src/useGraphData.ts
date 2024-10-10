import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import SerializedGraph from "./assets/graph.json";
import { SKILLS_MOCK } from "../public/skills-mock.ts";
import { useMemo } from "react";

const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: () => Promise.resolve(SerializedGraph),
    staleTime: Infinity,
  });
}

const useSkills = () => {
  return useQuery({
    queryKey: ['skills'],
    queryFn: async () => {
      const stored = localStorage.getItem('skills');
      if (stored) return JSON.parse(stored);
      localStorage.setItem('skillsData', JSON.stringify(SKILLS_MOCK));
      return SKILLS_MOCK;
    },
  });
}

const useUpdateSkill = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ nodeId, key, value }) => {
      const skills = queryClient.getQueryData(['skills']);
      const updatedSkills = {
        ...skills.data,
        [nodeId]: { ...skills.data[nodeId], [key]: value }
      };
      localStorage.setItem('skillsData', JSON.stringify(updatedSkills));
      return updatedSkills;
    },
    onSuccess: (updatedSkills) => {
      queryClient.setQueryData(['skills'], updatedSkills);
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
    setSkill: (nodeId, key, value) => updateSkillMutation.mutate({ nodeId, key, value }),
    refetchSkills: () => skillsQuery.refetch(),
    isLoading: categoriesQuery.isLoading || skillsQuery.isLoading,
    isError: categoriesQuery.isError || skillsQuery.isError || updateSkillMutation.isError
  };
}
