import apiClient from './client';

export interface Message {
  id: string;
  conversation: string;
  conversation_participant: string;
  platform: string;
  platform_message_id: string;
  message_type: 'text' | 'image' | 'video' | 'audio' | 'file' | 'sticker' | 'location';
  content: string;
  media_url?: string;
  sender_id: string;
  sender_name: string;
  is_incoming: boolean;
  is_read: boolean;
  read_at?: string;
  delivered_at?: string;
  sent_at: string;
  created_at: string;
}

export interface PaginatedMessages {
  count: number;
  next?: string;
  previous?: string;
  results: Message[];
}

export interface MessageFilters {
  conversation?: string;
  platform?: 'instagram' | 'messenger' | 'whatsapp';
  is_read?: boolean;
  page?: number;
  page_size?: number;
}

export const messagesApi = {
  /**
   * Get list of messages with optional filters
   */
  list: async (filters?: MessageFilters): Promise<PaginatedMessages> => {
    const params = new URLSearchParams();

    if (filters?.conversation) params.append('conversation', filters.conversation);
    if (filters?.platform) params.append('platform', filters.platform);
    if (filters?.is_read !== undefined) params.append('is_read', String(filters.is_read));
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.page_size) params.append('page_size', String(filters.page_size));

    const response = await apiClient.get<PaginatedMessages>(`/messages/messages/?${params}`);
    return response.data;
  },

  /**
   * Get a single message by ID
   */
  get: async (id: string): Promise<Message> => {
    const response = await apiClient.get<Message>(`/messages/messages/${id}/`);
    return response.data;
  },

  /**
   * Mark a message as read
   */
  markAsRead: async (id: string): Promise<{ message: string; data: Message }> => {
    const response = await apiClient.post<{ message: string; data: Message }>(
      `/messages/messages/${id}/mark-read/`
    );
    return response.data;
  },
};

export default messagesApi;
