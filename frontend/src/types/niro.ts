// ==========================================
// NIRO Chat Types
// ==========================================

// Suggested action from NIRO (quick reply chips)
export interface SuggestedAction {
  id: string;       // e.g., "focus_career", "ask_timing"
  label: string;    // text displayed on chip
}

// NIRO's structured reply
export interface NiroReply {
  rawText?: string;    // full message as plain text (optional)
  summary: string;     // summary paragraph
  reasons: string[];   // bullet points of reasons
  remedies: string[];  // remedies (may be empty)
}

// Backend response structure
export interface NiroChatResponse {
  reply: NiroReply;
  mode: string;           // e.g., "FOCUS_READING", "PAST_THEMES"
  focus: string | null;   // "career" | "relationship" | "health" | null
  suggestedActions: SuggestedAction[];
}

// Request payload to backend
export interface NiroChatRequest {
  sessionId: string;
  message: string;
  actionId?: string | null;  // optional action identifier
}

// Chat message types
export type MessageRole = 'user' | 'niro';

// User message
export interface UserChatMessage {
  id: string;
  role: 'user';
  content: string;
  timestamp: Date;
}

// NIRO message
export interface NiroChatMessage {
  id: string;
  role: 'niro';
  reply: NiroReply;
  mode: string;
  focus: string | null;
  suggestedActions: SuggestedAction[];
  timestamp: Date;
}

// Union type for all messages
export type ChatMessage = UserChatMessage | NiroChatMessage;

// Chat state
export interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
}
