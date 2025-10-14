import { Message, DailyMessageVolume } from '@/types/chat';

export const mockMessages: Message[] = [
  {
    id: '1',
    platform: 'instagram',
    contactName: 'Emma Smith',
    message: "Sure, I'll get back to you on that.",
    timestamp: '10:22',
    unread: false,
  },
  {
    id: '2',
    platform: 'messenger',
    contactName: 'Daniel Martinez',
    message: 'Thank you for the information!',
    timestamp: '09:45',
    unread: false,
  },
  {
    id: '3',
    platform: 'whatsapp',
    contactName: 'Sarah Johnson',
    message: 'Are you available for a call?',
    timestamp: 'Yesterday',
    unread: true,
  },
  {
    id: '4',
    platform: 'instagram',
    contactName: 'Michael Brown',
    message: 'Hello!',
    timestamp: 'Yesterday',
    unread: false,
  },
  {
    id: '5',
    platform: 'whatsapp',
    contactName: 'Lisa Anderson',
    message: 'Got it, thanks!',
    timestamp: 'Yesterday',
    unread: false,
  },
  {
    id: '6',
    platform: 'messenger',
    contactName: 'James Wilson',
    message: 'Perfect, see you then.',
    timestamp: 'Yesterday',
    unread: false,
  },
];

export const dailyMessageVolume: DailyMessageVolume[] = [
  { day: 'Mo', count: 45 },
  { day: 'Tu', count: 62 },
  { day: 'We', count: 51 },
  { day: 'Th', count: 58 },
  { day: 'Fr', count: 68 },
  { day: 'Sa', count: 55 },
  { day: 'Su', count: 72 },
];
