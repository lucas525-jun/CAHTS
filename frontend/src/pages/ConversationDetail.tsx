import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { conversationsApi, handleApiError } from '../services/api';
import { MessageComposer } from '../components/MessageComposer';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  Instagram,
  MessageCircle,
  MessageSquare,
  User,
  CheckCheck,
  Check,
  Image as ImageIcon,
  Video,
  File,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEffect, useRef } from 'react';

const ConversationDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch conversation details with messages
  const { data: conversation, isLoading, error } = useQuery({
    queryKey: ['conversation', id],
    queryFn: () => conversationsApi.get(id!),
    enabled: !!id,
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (data: { content: string; mediaUrl?: string; messageType?: string }) =>
      conversationsApi.sendMessage(id!, {
        content: data.content,
        message_type: (data.messageType as any) || 'text',
        media_url: data.mediaUrl,
      }),
    onSuccess: () => {
      // Refresh conversation to get new message
      queryClient.invalidateQueries({ queryKey: ['conversation', id] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      toast.success('Message sent!');
    },
    onError: (error) => {
      toast.error(handleApiError(error));
    },
  });

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages]);

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return <Instagram className="h-5 w-5" />;
      case 'messenger':
        return <MessageCircle className="h-5 w-5" />;
      case 'whatsapp':
        return <MessageSquare className="h-5 w-5" />;
      default:
        return <User className="h-5 w-5" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return 'from-instagram-start to-instagram-end';
      case 'messenger':
        return 'from-messenger to-messenger';
      case 'whatsapp':
        return 'from-whatsapp to-whatsapp';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getMessageIcon = (messageType: string) => {
    switch (messageType) {
      case 'image':
        return <ImageIcon className="h-4 w-4" />;
      case 'video':
        return <Video className="h-4 w-4" />;
      case 'file':
      case 'audio':
        return <File className="h-4 w-4" />;
      default:
        return null;
    }
  };

  if (error) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">Failed to load conversation</h2>
          <p className="text-muted-foreground mb-4">Please try again</p>
          <Button onClick={() => navigate('/chats')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Chats
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading conversation...</p>
        </div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">Conversation not found</h2>
          <Button onClick={() => navigate('/chats')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Chats
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="flex items-center gap-4 p-4 border-b bg-card">
        <Button variant="ghost" size="icon" onClick={() => navigate('/chats')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>

        <div className="flex items-center gap-3 flex-1">
          {conversation.participant_avatar ? (
            <img
              src={conversation.participant_avatar}
              alt={conversation.participant_name}
              className="h-10 w-10 rounded-full"
            />
          ) : (
            <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
              <User className="h-5 w-5 text-muted-foreground" />
            </div>
          )}

          <div className="flex-1">
            <h2 className="font-semibold text-lg">{conversation.participant_name}</h2>
            <div className="flex items-center gap-2">
              <div className={`p-1 rounded-full bg-gradient-to-r ${getPlatformColor(conversation.platform)}`}>
                <div className="text-white">
                  {getPlatformIcon(conversation.platform)}
                </div>
              </div>
              <Badge variant="outline" className="capitalize">
                {conversation.platform}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversation.messages && conversation.messages.length > 0 ? (
          <>
            {[...conversation.messages].reverse().map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex',
                  message.is_incoming ? 'justify-start' : 'justify-end'
                )}
              >
                <Card
                  className={cn(
                    'max-w-[70%] p-3',
                    message.is_incoming
                      ? 'bg-muted'
                      : 'bg-primary text-primary-foreground'
                  )}
                >
                  {/* Sender name for incoming messages */}
                  {message.is_incoming && (
                    <p className="text-xs font-semibold mb-1">{message.sender_name}</p>
                  )}

                  {/* Message content */}
                  <div className="space-y-2">
                    {message.message_type !== 'text' && message.media_url && (
                      <div className="flex items-center gap-2 text-sm">
                        {getMessageIcon(message.message_type)}
                        <span className="capitalize">{message.message_type}</span>
                      </div>
                    )}

                    {message.message_type === 'image' && message.media_url && (
                      <img
                        src={message.media_url}
                        alt="Message attachment"
                        className="rounded max-w-full"
                      />
                    )}

                    {message.content && (
                      <p className="whitespace-pre-wrap break-words">{message.content}</p>
                    )}
                  </div>

                  {/* Message metadata */}
                  <div
                    className={cn(
                      'flex items-center justify-end gap-1 mt-2 text-xs',
                      message.is_incoming
                        ? 'text-muted-foreground'
                        : 'text-primary-foreground/70'
                    )}
                  >
                    <span>
                      {new Date(message.sent_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                    {!message.is_incoming && (
                      <>
                        {message.is_read ? (
                          <CheckCheck className="h-3 w-3" />
                        ) : message.delivered_at ? (
                          <CheckCheck className="h-3 w-3" />
                        ) : (
                          <Check className="h-3 w-3" />
                        )}
                      </>
                    )}
                  </div>
                </Card>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No messages yet</p>
              <p className="text-sm">Start the conversation!</p>
            </div>
          </div>
        )}
      </div>

      {/* Message Composer */}
      <MessageComposer
        onSend={(content, mediaUrl, messageType) =>
          sendMessageMutation.mutate({ content, mediaUrl, messageType })
        }
        loading={sendMessageMutation.isPending}
        placeholder={`Message ${conversation.participant_name}...`}
      />
    </div>
  );
};

export default ConversationDetail;
