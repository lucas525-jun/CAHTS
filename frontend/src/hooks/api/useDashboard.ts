import { useQuery } from '@tanstack/react-query';
import { platformsApi, analyticsApi } from '../../services/api';

/**
 * Hook to fetch connected platforms
 */
export const usePlatforms = () => {
  return useQuery({
    queryKey: ['platforms'],
    queryFn: () => platformsApi.list(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to fetch dashboard statistics from analytics API
 */
export const useDashboardStats = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['analytics', 'stats'],
    queryFn: () => analyticsApi.getMessageStats(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const stats = {
    totalMessages: data?.total_messages || 0,
    unreadMessages: data?.unread_messages || 0,
    totalConversations: data?.total_conversations || 0,
    instagram: data?.platform_breakdown?.instagram || 0,
    messenger: data?.platform_breakdown?.messenger || 0,
    whatsapp: data?.platform_breakdown?.whatsapp || 0,
  };

  return {
    stats,
    isLoading,
    error,
  };
};

/**
 * Hook to fetch daily statistics
 */
export const useDailyStats = (days: number = 7) => {
  return useQuery({
    queryKey: ['analytics', 'daily', days],
    queryFn: () => analyticsApi.getDailyStats(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
