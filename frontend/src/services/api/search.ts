import apiClient from './client';
import { Message } from './messages';
import { Conversation } from './conversations';

export interface SearchFilters {
  q: string;
  platform?: 'instagram' | 'messenger' | 'whatsapp';
  is_read?: boolean;
  limit?: number;
}

export interface SearchResults {
  query: string;
  results: {
    messages: Message[];
    conversations: Conversation[];
    total_messages: number;
    total_conversations: number;
  };
}

export const searchApi = {
  /**
   * Search messages and conversations
   */
  search: async (filters: SearchFilters): Promise<SearchResults> => {
    const params = new URLSearchParams();
    params.append('q', filters.q);

    if (filters.platform) params.append('platform', filters.platform);
    if (filters.is_read !== undefined) params.append('is_read', String(filters.is_read));
    if (filters.limit) params.append('limit', String(filters.limit));

    const response = await apiClient.get<SearchResults>(`/messages/search/?${params}`);
    return response.data;
  },
};

export default searchApi;
