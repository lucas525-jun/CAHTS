import apiClient from './client';
import { Message } from './messages';

export interface Conversation {
  id: string;
  platform: string;
  platform_conversation_id: string;
  participant_id: string;
  participant_name: string;
  participant_avatar?: string;
  last_message_at: string;
  unread_count: number;
  is_archived: boolean;
  last_message?: {
    id: string;
    content: string;
    sender_name: string;
    sent_at: string;
    is_read: boolean;
  };
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface PaginatedConversations {
  count: number;
  next?: string;
  previous?: string;
  results: Conversation[];
}

export interface ConversationFilters {
  platform?: 'instagram' | 'messenger' | 'whatsapp';
  is_archived?: boolean;
  page?: number;
  page_size?: number;
}

export interface SendMessageData {
  content: string;
  message_type?: 'text' | 'image' | 'video' | 'audio' | 'file';
  media_url?: string;
}

export const conversationsApi = {
  /**
   * Get list of conversations with optional filters
   */
  list: async (filters?: ConversationFilters): Promise<PaginatedConversations> => {
    const params = new URLSearchParams();

    if (filters?.platform) params.append('platform', filters.platform);
    if (filters?.is_archived !== undefined) params.append('is_archived', String(filters.is_archived));
    if (filters?.page) params.append('page', String(filters.page));
    if (filters?.page_size) params.append('page_size', String(filters.page_size));

    const response = await apiClient.get<PaginatedConversations>(`/messages/conversations/?${params}`);
    return response.data;
  },

  /**
   * Get a single conversation with recent messages
   */
  get: async (id: string, messagesLimit: number = 50): Promise<ConversationDetail> => {
    const response = await apiClient.get<ConversationDetail>(
      `/messages/conversations/${id}/?messages_limit=${messagesLimit}`
    );
    return response.data;
  },

  /**
   * Mark all messages in a conversation as read
   */
  markAllAsRead: async (id: string): Promise<{ message: string; conversation: Conversation }> => {
    const response = await apiClient.post<{ message: string; conversation: Conversation }>(
      `/messages/conversations/${id}/mark-all-read/`
    );
    return response.data;
  },

  /**
   * Archive a conversation
   */
  archive: async (id: string): Promise<{ message: string; conversation: Conversation }> => {
    const response = await apiClient.post<{ message: string; conversation: Conversation }>(
      `/messages/conversations/${id}/archive/`
    );
    return response.data;
  },

  /**
   * Unarchive a conversation
   */
  unarchive: async (id: string): Promise<{ message: string; conversation: Conversation }> => {
    const response = await apiClient.post<{ message: string; conversation: Conversation }>(
      `/messages/conversations/${id}/unarchive/`
    );
    return response.data;
  },

  /**
   * Send a message in a conversation
   */
  sendMessage: async (id: string, data: SendMessageData): Promise<{ message: string; data: Message }> => {
    const response = await apiClient.post<{ message: string; data: Message }>(
      `/messages/conversations/${id}/send-message/`,
      data
    );
    return response.data;
  },
};

export default conversationsApi;
