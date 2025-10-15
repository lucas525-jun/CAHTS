import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { conversationsApi, type ConversationFilters } from '../../services/api';
import { useState, useEffect } from 'react';
import { websocketService } from '../../services/websocket';
import type { Message } from '../../services/api/messages';

/**
 * Hook to fetch conversations with optional filters
 */
export const useConversationsList = (filters?: ConversationFilters) => {
  return useQuery({
    queryKey: ['conversations', filters],
    queryFn: () => conversationsApi.list(filters),
    staleTime: 30 * 1000, // 30 seconds
  });
};

/**
 * Hook to fetch a single conversation with messages
 */
export const useConversation = (id: string | null, messagesLimit: number = 50) => {
  return useQuery({
    queryKey: ['conversation', id, messagesLimit],
    queryFn: () => conversationsApi.get(id!, messagesLimit),
    enabled: !!id,
    staleTime: 10 * 1000, // 10 seconds
  });
};

/**
 * Hook to mark all messages in a conversation as read
 */
export const useMarkAllAsRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => conversationsApi.markAllAsRead(id),
    onSuccess: (_, id) => {
      // Invalidate conversations list and specific conversation
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['conversation', id] });
    },
  });
};

/**
 * Hook to archive/unarchive a conversation
 */
export const useArchiveConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, archive }: { id: string; archive: boolean }) =>
      archive ? conversationsApi.archive(id) : conversationsApi.unarchive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

/**
 * Hook for WebSocket real-time message updates
 */
export const useRealtimeMessages = (onNewMessage?: (message: Message) => void) => {
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Handle new messages
    const unsubscribeMessage = websocketService.onMessage((message) => {
      // Invalidate conversations to update unread counts
      queryClient.invalidateQueries({ queryKey: ['conversations'] });

      // Invalidate the specific conversation if it exists
      if (message.conversation) {
        queryClient.invalidateQueries({ queryKey: ['conversation', message.conversation] });
      }

      // Call custom callback if provided
      if (onNewMessage) {
        onNewMessage(message);
      }
    });

    // Handle connection state
    const unsubscribeConnect = websocketService.onConnect(() => {
      setIsConnected(true);
    });

    const unsubscribeDisconnect = websocketService.onDisconnect(() => {
      setIsConnected(false);
    });

    // Update initial connection state
    setIsConnected(websocketService.isConnected());

    // Cleanup on unmount
    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
    };
  }, [queryClient, onNewMessage]);

  return { isConnected };
};
