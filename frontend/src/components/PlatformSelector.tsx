import { Platform } from '@/types/chat';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { InstagramIcon, MessengerIcon, WhatsAppIcon } from '@/components/icons/PlatformIcons';

interface PlatformSelectorProps {
  selectedPlatform: Platform | 'all';
  onSelectPlatform: (platform: Platform | 'all') => void;
}

export const PlatformSelector = ({ selectedPlatform, onSelectPlatform }: PlatformSelectorProps) => {
  const platforms: { id: Platform | 'all'; label: string; icon: any; gradient?: string }[] = [
    { id: 'instagram', label: 'Instagram', icon: InstagramIcon, gradient: 'from-instagram-start to-instagram-end' },
    { id: 'messenger', label: 'Messenger', icon: MessengerIcon },
    { id: 'whatsapp', label: 'WhatsApp', icon: WhatsAppIcon },
  ];

  return (
    <div className="w-64 border-r border-border bg-card p-4 space-y-2">
      <h2 className="text-2xl font-bold mb-6">Chats</h2>
      {platforms.map((platform) => (
        <Button
          key={platform.id}
          variant={selectedPlatform === platform.id ? 'default' : 'ghost'}
          className={cn(
            'w-full justify-start gap-3 h-14',
            selectedPlatform === platform.id && platform.gradient && `bg-gradient-to-r ${platform.gradient} text-white hover:opacity-90`,
            selectedPlatform === platform.id && platform.id === 'messenger' && 'bg-messenger text-white hover:bg-messenger/90',
            selectedPlatform === platform.id && platform.id === 'whatsapp' && 'bg-whatsapp text-white hover:bg-whatsapp/90'
          )}
          onClick={() => onSelectPlatform(platform.id)}
        >
          <platform.icon className="h-6 w-6" />
          <span className="font-medium">{platform.label}</span>
        </Button>
      ))}
    </div>
  );
};
