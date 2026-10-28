import { useQuery } from "@tanstack/react-query";
import { getProfile } from "@/services/profileServices";

export const useProfile = () => {
  const query = useQuery({
    queryKey: ["profile"],
    queryFn: getProfile,
  });

  return {
    profile: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
};