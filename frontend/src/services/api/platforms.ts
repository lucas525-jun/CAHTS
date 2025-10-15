import apiClient from './client';

export interface PlatformAccount {
  id: string;
  platform: 'instagram' | 'messenger' | 'whatsapp';
  platform_user_id: string;
  username: string;
  is_active: boolean;
  last_sync_at?: string;
  metadata: Record<string, any>;
  connected_at: string;
}

export const platformsApi = {
  /**
   * Get list of connected platform accounts
   */
  list: async (): Promise<PlatformAccount[]> => {
    const response = await apiClient.get<PlatformAccount[]>('/platforms/');
    return response.data;
  },

  /**
   * Connect Instagram account - initiates OAuth flow
   */
  connectInstagram: async (): Promise<{ auth_url: string }> => {
    const response = await apiClient.post<{ auth_url: string }>('/platforms/connect/instagram/');
    return response.data;
  },

  /**
   * Connect Messenger account - initiates OAuth flow
   */
  connectMessenger: async (): Promise<{ auth_url: string }> => {
    const response = await apiClient.post<{ auth_url: string }>('/platforms/connect/messenger/');
    return response.data;
  },

  /**
   * Connect WhatsApp account
   */
  connectWhatsApp: async (phoneNumber: string, accessToken: string): Promise<PlatformAccount> => {
    const response = await apiClient.post<PlatformAccount>('/platforms/connect/whatsapp/', {
      phone_number: phoneNumber,
      access_token: accessToken,
    });
    return response.data;
  },

  /**
   * Disconnect a platform account
   */
  disconnect: async (id: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/platforms/${id}/disconnect/`);
    return response.data;
  },

  /**
   * Trigger manual sync for a platform
   */
  sync: async (id: string): Promise<{ message: string; task_id?: string }> => {
    const response = await apiClient.post<{ message: string; task_id?: string }>(
      `/platforms/${id}/sync/`
    );
    return response.data;
  },
};

export default platformsApi;
