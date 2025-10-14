import { useState } from 'react';
import { PlatformSelector } from '@/components/PlatformSelector';
import { MessageList } from '@/components/MessageList';
import { StatsPanel } from '@/components/StatsPanel';
import { mockMessages, dailyMessageVolume } from '@/data/mockData';
import { Platform, PlatformStats } from '@/types/chat';

const Chats = () => {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | 'all'>('all');

  const platformStats: PlatformStats[] = [
    { platform: 'instagram', count: mockMessages.filter(m => m.platform === 'instagram').length },
    { platform: 'whatsapp', count: mockMessages.filter(m => m.platform === 'whatsapp').length },
    { platform: 'messenger', count: mockMessages.filter(m => m.platform === 'messenger').length },
  ];

  return (
    <div className="flex h-screen bg-background">
      <PlatformSelector
        selectedPlatform={selectedPlatform}
        onSelectPlatform={setSelectedPlatform}
      />
      <MessageList messages={mockMessages} selectedPlatform={selectedPlatform} />
      <StatsPanel platformStats={platformStats} dailyVolume={dailyMessageVolume} />
    </div>
  );
};

export default Chats;
