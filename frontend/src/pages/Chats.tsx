import { useState } from 'react';
import { PlatformSelector } from '@/components/PlatformSelector';
import { MessageList } from '@/components/MessageList';
import { StatsPanel } from '@/components/StatsPanel';
import { Platform, PlatformStats } from '@/types/chat';
import { useConversationsList, useRealtimeMessages } from '../hooks/api/useChats';
import { Loader2, AlertCircle, MessageSquare, Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { searchApi } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Chats = () => {
  const navigate = useNavigate();
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Fetch conversations with optional platform filter
  const filters = selectedPlatform !== 'all' ? { platform: selectedPlatform } : undefined;
  const { data: conversationsData, isLoading, error, refetch } = useConversationsList(filters);

  // Subscribe to real-time WebSocket messages
  const { isConnected } = useRealtimeMessages((message) => {
    // Show toast notification for new messages
    if (message.is_incoming) {
      toast.info(`New message from ${message.sender_name}`, {
        description: message.content.substring(0, 50) + (message.content.length > 50 ? '...' : ''),
      });
    }
  });

  // Search query
  const { data: searchResults, isLoading: isSearchLoading } = useQuery({
    queryKey: ['search', searchQuery, selectedPlatform],
    queryFn: () =>
      searchApi.search({
        q: searchQuery,
        platform: selectedPlatform !== 'all' ? selectedPlatform : undefined,
        limit: 50,
      }),
    enabled: searchQuery.length >= 2,
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setIsSearching(query.length >= 2);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setIsSearching(false);
  };

  // Calculate platform stats
  const allConversations = conversationsData?.results || [];
  const platformStats: PlatformStats[] = [
    {
      platform: 'instagram',
      count: allConversations.filter((c) => c.platform.toLowerCase() === 'instagram').length,
    },
    {
      platform: 'whatsapp',
      count: allConversations.filter((c) => c.platform.toLowerCase() === 'whatsapp').length,
    },
    {
      platform: 'messenger',
      count: allConversations.filter((c) => c.platform.toLowerCase() === 'messenger').length,
    },
  ];

  // Mock daily volume (will be replaced with real API data)
  const dailyMessageVolume = [
    { day: 'Mon', count: 45 },
    { day: 'Tue', count: 52 },
    { day: 'Wed', count: 48 },
    { day: 'Thu', count: 61 },
    { day: 'Fri', count: 55 },
    { day: 'Sat', count: 38 },
    { day: 'Sun', count: 42 },
  ];

  // Convert conversations to messages format for MessageList component
  const messages = allConversations.map((conv) => ({
    id: conv.id,
    platform: conv.platform.toLowerCase() as Platform,
    sender: conv.participant_name,
    content: conv.last_message?.content || 'No messages yet',
    timestamp: new Date(conv.last_message_at).toLocaleString(),
    avatar: conv.participant_avatar,
    unread: conv.unread_count > 0,
  }));

  if (error) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">Failed to load conversations</h2>
          <p className="text-muted-foreground mb-4">Please try refreshing the page</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-screen bg-background items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading conversations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <PlatformSelector
        selectedPlatform={selectedPlatform}
        onSelectPlatform={(platform) => {
          setSelectedPlatform(platform);
          if (isSearching) clearSearch();
        }}
      />

      {isSearching ? (
        <div className="flex-1 flex flex-col overflow-hidden lg:pl-0 pl-16">
          {/* Search Header */}
          <div className="flex items-center gap-3 p-4 border-b">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search messages and conversations..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 pr-10"
                autoFocus
              />
              {searchQuery && (
                <button
                  onClick={clearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                >
                  <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                </button>
              )}
            </div>
          </div>

          {/* Search Results */}
          <div className="flex-1 overflow-y-auto p-6">
            {isSearchLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : searchResults ? (
              <div className="space-y-6">
                {/* Conversations Results */}
                {searchResults.results.conversations.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      Conversations
                      <Badge variant="secondary">
                        {searchResults.results.total_conversations}
                      </Badge>
                    </h3>
                    <div className="space-y-2">
                      {searchResults.results.conversations.map((conv) => (
                        <Card
                          key={conv.id}
                          className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                          onClick={() => navigate(`/chats/${conv.id}`)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h4 className="font-semibold">{conv.participant_name}</h4>
                                <Badge variant="outline" className="capitalize text-xs">
                                  {conv.platform}
                                </Badge>
                              </div>
                              {conv.last_message && (
                                <p className="text-sm text-muted-foreground">
                                  {conv.last_message.content}
                                </p>
                              )}
                            </div>
                            {conv.unread_count > 0 && (
                              <Badge variant="destructive">{conv.unread_count}</Badge>
                            )}
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Messages Results */}
                {searchResults.results.messages.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      Messages
                      <Badge variant="secondary">
                        {searchResults.results.total_messages}
                      </Badge>
                    </h3>
                    <div className="space-y-2">
                      {searchResults.results.messages.map((msg) => (
                        <Card
                          key={msg.id}
                          className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                          onClick={() => navigate(`/chats/${msg.conversation}`)}
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-sm">{msg.sender_name}</span>
                              <Badge variant="outline" className="capitalize text-xs">
                                {msg.platform}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                {new Date(msg.sent_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-sm">{msg.content}</p>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Results */}
                {searchResults.results.conversations.length === 0 &&
                  searchResults.results.messages.length === 0 && (
                    <div className="text-center py-12">
                      <Search className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                      <h3 className="text-lg font-semibold mb-2">No results found</h3>
                      <p className="text-muted-foreground">
                        Try different keywords or check your filters
                      </p>
                    </div>
                  )}
              </div>
            ) : (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">Start typing to search...</p>
              </div>
            )}
          </div>
        </div>
      ) : messages.length > 0 ? (
        <>
          {/* Search Bar and Messages */}
          <div className="flex-1 flex flex-col overflow-hidden lg:pl-0 pl-16">
            <div className="p-4 border-b">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search messages and conversations..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <MessageList messages={messages} selectedPlatform={selectedPlatform} />
          </div>

          {/* Stats Panel - Hidden on mobile/tablet, visible on large screens */}
          <div className="hidden xl:block">
            <StatsPanel platformStats={platformStats} dailyVolume={dailyMessageVolume} />
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center lg:pl-0 pl-16">
          <div className="text-center max-w-md px-4">
            <MessageSquare className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No conversations yet</h3>
            <p className="text-muted-foreground mb-4">
              {selectedPlatform === 'all'
                ? 'Connect a platform to start receiving messages'
                : `No ${selectedPlatform} conversations found`}
            </p>
            {selectedPlatform !== 'all' && (
              <button
                onClick={() => setSelectedPlatform('all')}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              >
                View all platforms
              </button>
            )}
          </div>
        </div>
      )}

      {/* WebSocket connection indicator */}
      <div className="fixed bottom-4 right-4 flex items-center gap-2 px-3 py-2 bg-card rounded-full shadow-lg border z-40">
        <div
          className={`h-2 w-2 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
          }`}
        />
        <span className="text-xs text-muted-foreground hidden sm:inline">
          {isConnected ? 'Live' : 'Connecting...'}
        </span>
      </div>
    </div>
  );
};

export default Chats;
