import { useQuery } from "@tanstack/react-query";
import { SkillResources } from "./types.ts";

interface UseSkillDescriptionProps {
  skill: string,
}

const fetchSkillResources = async (skill: string): Promise<SkillResources> => {
  return Promise.resolve({
    description: 'This is a very important skill. You should definitely learn it.'
  });
}

export const useSkillResources = ({ skill }: UseSkillDescriptionProps) => {
  return useQuery({
    queryKey: ['descriptions', skill],
    queryFn: () => fetchSkillResources(skill),
    staleTime: Infinity,
  });
};
