import { useQuery } from '@tanstack/react-query';
import { conversationsApi, platformsApi } from '../../services/api';

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
 * Hook to fetch conversations with statistics
 */
export const useConversations = () => {
  return useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationsApi.list({ page_size: 100 }),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

/**
 * Calculate dashboard statistics from conversations
 */
export const useDashboardStats = () => {
  const { data: conversationsData, isLoading, error } = useConversations();

  const stats = {
    totalMessages: 0,
    unreadMessages: 0,
    totalConversations: conversationsData?.count || 0,
    instagram: 0,
    messenger: 0,
    whatsapp: 0,
  };

  if (conversationsData?.results) {
    conversationsData.results.forEach((conv) => {
      // Count unread messages
      stats.unreadMessages += conv.unread_count;

      // Count by platform
      const platform = conv.platform.toLowerCase();
      if (platform === 'instagram') stats.instagram++;
      else if (platform === 'messenger') stats.messenger++;
      else if (platform === 'whatsapp') stats.whatsapp++;
    });
  }

  return {
    stats,
    isLoading,
    error,
  };
};
