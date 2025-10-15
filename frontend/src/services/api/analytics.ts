import apiClient from './client';

export interface MessageStats {
  total_messages: number;
  unread_messages: number;
  total_conversations: number;
  platform_breakdown: {
    instagram: number;
    messenger: number;
    whatsapp: number;
  };
}

export interface DailyStats {
  date: string;
  message_count: number;
  conversation_count: number;
}

export const analyticsApi = {
  /**
   * Get message statistics
   */
  getMessageStats: async (): Promise<MessageStats> => {
    const response = await apiClient.get<MessageStats>('/analytics/stats/messages/');
    return response.data;
  },

  /**
   * Get daily statistics for the last N days
   */
  getDailyStats: async (days: number = 7): Promise<DailyStats[]> => {
    const response = await apiClient.get<DailyStats[]>(`/analytics/stats/daily/?days=${days}`);
    return response.data;
  },
};

export default analyticsApi;
