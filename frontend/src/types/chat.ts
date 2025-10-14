export type Platform = 'instagram' | 'messenger' | 'whatsapp';

export interface Message {
  id: string;
  platform: Platform;
  contactName: string;
  message: string;
  timestamp: string;
  unread?: boolean;
}

export interface PlatformStats {
  platform: Platform;
  count: number;
}

export interface DailyMessageVolume {
  day: string;
  count: number;
}
