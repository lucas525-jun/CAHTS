import { Message } from './api/messages';

type MessageHandler = (message: Message) => void;
type ErrorHandler = (error: Event) => void;
type ConnectionHandler = () => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private connectHandlers: Set<ConnectionHandler> = new Set();
  private disconnectHandlers: Set<ConnectionHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private reconnectTimeout: number | null = null;
  private userId: string | null = null;

  /**
   * Connect to WebSocket server
   */
  connect(userId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.userId = userId;
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const token = localStorage.getItem('access_token');

    // CRITICAL: Check if token exists
    if (!token) {
      console.error('❌ No access token found in localStorage. Cannot connect to WebSocket.');
      console.error('Please ensure you are logged in and have a valid token.');
      return;
    }

    // Construct WebSocket URL with user ID and token (URL encode the token)
    const url = `${wsUrl}/messages/${userId}/?token=${encodeURIComponent(token)}`;

    console.log('🔌 Connecting to WebSocket...');
    console.log('  User ID:', userId);
    console.log('  Token length:', token.length);
    console.log('  Token preview:', token.substring(0, 20) + '...');

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected successfully!');
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;

      this.connectHandlers.forEach((handler) => handler());
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle different message types
        if (data.type === 'new_message' && data.message) {
          this.messageHandlers.forEach((handler) => handler(data.message));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.errorHandlers.forEach((handler) => handler(error));
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.disconnectHandlers.forEach((handler) => handler());

      // Attempt to reconnect
      this.attemptReconnect();
    };
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.userId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(): void {
    if (!this.userId) {
      console.log('No user ID, skipping reconnect');
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.connect(this.userId!);
    }, delay);
  }

  /**
   * Subscribe to new messages
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to connection events
   */
  onConnect(handler: ConnectionHandler): () => void {
    this.connectHandlers.add(handler);

    return () => {
      this.connectHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to disconnection events
   */
  onDisconnect(handler: ConnectionHandler): () => void {
    this.disconnectHandlers.add(handler);

    return () => {
      this.disconnectHandlers.delete(handler);
    };
  }

  /**
   * Subscribe to error events
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);

    return () => {
      this.errorHandlers.delete(handler);
    };
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

export default websocketService;
