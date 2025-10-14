import { Message, Platform } from '@/types/chat';
import { Instagram, MessageCircle, MessageSquare } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface MessageListProps {
  messages: Message[];
  selectedPlatform: Platform | 'all';
}

const platformIcons = {
  instagram: Instagram,
  messenger: MessageCircle,
  whatsapp: MessageSquare,
};

const platformColors = {
  instagram: 'text-instagram-start',
  messenger: 'text-messenger',
  whatsapp: 'text-whatsapp',
};

export const MessageList = ({ messages, selectedPlatform }: MessageListProps) => {
  const filteredMessages = selectedPlatform === 'all' 
    ? messages 
    : messages.filter(m => m.platform === selectedPlatform);

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="space-y-3">
        {filteredMessages.map((message) => {
          const Icon = platformIcons[message.platform];
          return (
            <Card
              key={message.id}
              className={cn(
                'p-4 hover:shadow-md transition-shadow cursor-pointer',
                message.unread && 'border-l-4 border-l-primary'
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <Icon className={cn('h-5 w-5 mt-1', platformColors[message.platform])} />
                  <div className="flex-1">
                    <h3 className="font-semibold text-card-foreground">{message.contactName}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{message.message}</p>
                  </div>
                </div>
                <span className="text-sm text-muted-foreground">{message.timestamp}</span>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
