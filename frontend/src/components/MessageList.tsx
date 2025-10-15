import { Message, Platform } from '@/types/chat';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';
import { InstagramIcon, MessengerIcon, WhatsAppIcon } from '@/components/icons/PlatformIcons';

interface MessageListProps {
  messages: Message[];
  selectedPlatform: Platform | 'all';
}

const platformIcons = {
  instagram: InstagramIcon,
  messenger: MessengerIcon,
  whatsapp: WhatsAppIcon,
};

const platformColors = {
  instagram: 'text-instagram-start',
  messenger: 'text-messenger',
  whatsapp: 'text-whatsapp',
};

export const MessageList = ({ messages, selectedPlatform }: MessageListProps) => {
  const navigate = useNavigate();

  const filteredMessages = selectedPlatform === 'all'
    ? messages
    : messages.filter(m => m.platform === selectedPlatform);

  const handleMessageClick = (conversationId: string) => {
    navigate(`/chats/${conversationId}`);
  };

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
              onClick={() => handleMessageClick(message.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <Icon className={cn('h-5 w-5 mt-1', platformColors[message.platform])} />
                  <div className="flex-1">
                    <h3 className="font-semibold text-card-foreground">{message.sender}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{message.content}</p>
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
