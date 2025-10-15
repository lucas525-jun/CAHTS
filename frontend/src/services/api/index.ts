export { default as apiClient, handleApiError, setAuthTokens, clearAuthTokens, isAuthenticated } from './client';
export { default as authApi } from './auth';
export { default as messagesApi } from './messages';
export { default as conversationsApi } from './conversations';
export { default as platformsApi } from './platforms';
export { default as analyticsApi } from './analytics';
export { default as uploadApi } from './upload';
export { default as searchApi } from './search';

export type { RegisterData, LoginData, AuthResponse, User } from './auth';
export type { Message, PaginatedMessages, MessageFilters } from './messages';
export type { Conversation, ConversationDetail, PaginatedConversations, ConversationFilters, SendMessageData } from './conversations';
export type { PlatformAccount } from './platforms';
export type { MessageStats, DailyStats } from './analytics';
export type { UploadResponse, UploadLimits } from './upload';
export type { SearchFilters, SearchResults } from './search';
