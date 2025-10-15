import apiClient from './client';

export interface UploadResponse {
  message: string;
  data: {
    media_url: string;
    file_type: 'image' | 'video' | 'audio' | 'file';
    file_name: string;
    file_size: number;
    content_type: string;
  };
}

export interface UploadLimits {
  max_file_size: number;
  max_video_size: number;
  allowed_types: {
    image: string[];
    video: string[];
    audio: string[];
    document: string[];
  };
}

export const uploadApi = {
  /**
   * Upload a file for message attachment
   */
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>('/messages/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get file upload limits and allowed types
   */
  getUploadLimits: async (): Promise<UploadLimits> => {
    const response = await apiClient.get<UploadLimits>('/messages/upload/limits/');
    return response.data;
  },
};

export default uploadApi;
