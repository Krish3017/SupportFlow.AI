'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTheme } from 'next-themes';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Message } from '@/types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Moon, Sun, Loader2, UserCheck, LogOut, User } from 'lucide-react';
import {
  sendChatMessage,
  fetchConversationHistory,
  fetchSessionConversation,
  registerCustomer,
  loginCustomer,
  logoutCustomer,
  getAuthenticatedCustomer,
  AuthUser,
} from '@/lib/api';

const STORAGE_KEYS = {
  SESSION_ID: 'supportflow_session_id',
  CONVERSATION_ID: 'supportflow_conversation_id',
  AUTH_TOKEN: 'supportflow_auth_token',
} as const;

function getStoredSessionId(): string {
  if (typeof window === 'undefined') return '';
  let sessionId = localStorage.getItem(STORAGE_KEYS.SESSION_ID);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
  }
  return sessionId;
}

function getStoredConversationId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(STORAGE_KEYS.CONVERSATION_ID);
}

function storeConversationId(id: string) {
  localStorage.setItem(STORAGE_KEYS.CONVERSATION_ID, id);
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const { theme, setTheme } = useTheme();
  const sessionIdRef = useRef<string>('');
  const conversationIdRef = useRef<string | null>(null);
  const restoredRef = useRef(false);

  // Auth States
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [authToken, setAuthToken] = useState<string>('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [emailInput, setEmailInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [nameInput, setNameInput] = useState('');
  const [authError, setAuthError] = useState('');

  const restoreSession = useCallback(async () => {
    if (restoredRef.current) return;
    restoredRef.current = true;

    const sessionId = getStoredSessionId();
    sessionIdRef.current = sessionId;

    let currentToken = '';
    let currentUser: AuthUser | null = null;

    // Check stored auth token
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      currentToken = token;
      setAuthToken(token);
      const user = await getAuthenticatedCustomer(token);
      if (user) {
        currentUser = user;
        setAuthUser(user);
      } else {
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
      }
    }

    const storedConvId = getStoredConversationId();

    if (storedConvId) {
      const history = await fetchConversationHistory(storedConvId, currentToken);
      if (history && history.status !== 'closed' && history.status !== 'archived') {
        conversationIdRef.current = storedConvId;
        const restored: Message[] = history.messages.map((m) => ({
          id: m.id,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(restored);
        setIsRestoring(false);
        return;
      } else {
        // Clear stale/unauthorized stored conversation ID
        localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
        conversationIdRef.current = null;
      }
    }

    const sessionInfo = await fetchSessionConversation(sessionId);
    if (sessionInfo.conversation_id) {
      const history = await fetchConversationHistory(sessionInfo.conversation_id, currentToken);
      if (history && history.status !== 'closed' && history.status !== 'archived') {
        conversationIdRef.current = sessionInfo.conversation_id;
        storeConversationId(sessionInfo.conversation_id);
        const restored: Message[] = history.messages.map((m) => ({
          id: m.id,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(m.timestamp),
        }));
        setMessages(restored);
      }
    }

    setIsRestoring(false);
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      let res;
      if (authMode === 'register') {
        res = await registerCustomer(emailInput, passwordInput, nameInput);
      } else {
        res = await loginCustomer(emailInput, passwordInput);
      }
      setAuthToken(res.token);
      setAuthUser(res.user);
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, res.token);
      setShowAuthModal(false);
      setEmailInput('');
      setPasswordInput('');
      setNameInput('');

      // Refresh chat session for authenticated customer
      localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
      conversationIdRef.current = null;
      restoredRef.current = false;
      setIsRestoring(true);
      restoreSession();
    } catch (err: any) {
      setAuthError(err.message || 'Authentication failed.');
    }
  };

  const handleLogout = async () => {
    await logoutCustomer(authToken);
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
    setAuthToken('');
    setAuthUser(null);
    conversationIdRef.current = null;
    setMessages([]);
  };

  const handleNewChat = () => {
    localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
    conversationIdRef.current = null;
    const newSessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);
    sessionIdRef.current = newSessionId;
    setMessages([]);
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    const activeCustomerId = authUser ? authUser.email : 'anonymous';

    try {
      const result = await sendChatMessage(
        content,
        sessionIdRef.current,
        activeCustomerId,
        (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        authToken
      );

      if (result.session_id) {
        sessionIdRef.current = result.session_id;
        localStorage.setItem(STORAGE_KEYS.SESSION_ID, result.session_id);
      }

      if (result.conversation_id) {
        conversationIdRef.current = result.conversation_id;
        storeConversationId(result.conversation_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content:
                  'Sorry, I encountered an error. Please make sure the backend server is running.',
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl h-[650px] flex flex-col shadow-lg relative">
      {/* Header */}
      <div className="px-6 py-4 border-b bg-muted/40 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            SupportFlow AI
          </h2>
          <p className="text-xs text-muted-foreground">
            {authUser ? (
              <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                Logged in as {authUser.name || authUser.email}
              </span>
            ) : (
              <span>Guest Session (Login to view account data)</span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleNewChat} className="flex items-center gap-1">
            New Chat
          </Button>

          {authUser ? (
            <Button variant="outline" size="sm" onClick={handleLogout} className="flex items-center gap-1">
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          ) : (
            <Button variant="default" size="sm" onClick={() => setShowAuthModal(true)} className="flex items-center gap-1">
              <User className="h-4 w-4" />
              Sign In
            </Button>
          )}

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>

      {/* Auth Modal Overlay */}
      {showAuthModal && (
        <div className="absolute inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 shadow-2xl bg-card border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">
                {authMode === 'login' ? 'Customer Login' : 'Create Customer Account'}
              </h3>
              <Button variant="ghost" size="sm" onClick={() => setShowAuthModal(false)}>✕</Button>
            </div>

            {authError && (
              <div className="mb-4 p-2 text-xs bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300 rounded">
                {authError}
              </div>
            )}

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {authMode === 'register' && (
                <div>
                  <label className="text-xs font-medium block mb-1">Full Name</label>
                  <Input
                    type="text"
                    placeholder="Alice Johnson"
                    value={nameInput}
                    onChange={(e) => setNameInput(e.target.value)}
                  />
                </div>
              )}

              <div>
                <label className="text-xs font-medium block mb-1">Email Address</label>
                <Input
                  type="email"
                  required
                  placeholder="alice.johnson@example.com"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                />
              </div>

              <div>
                <label className="text-xs font-medium block mb-1">Password</label>
                <Input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                />
              </div>

              <Button type="submit" className="w-full">
                {authMode === 'login' ? 'Sign In' : 'Register Account'}
              </Button>
            </form>

            <div className="mt-4 text-center text-xs">
              {authMode === 'login' ? (
                <span>
                  Don't have an account?{' '}
                  <button
                    className="text-primary underline font-medium"
                    onClick={() => { setAuthMode('register'); setAuthError(''); }}
                  >
                    Register
                  </button>
                </span>
              ) : (
                <span>
                  Already have an account?{' '}
                  <button
                    className="text-primary underline font-medium"
                    onClick={() => { setAuthMode('login'); setAuthError(''); }}
                  >
                    Sign In
                  </button>
                </span>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-hidden">
        {isRestoring ? (
          <div className="h-full flex items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
      </div>

      <MessageInput onSendMessage={handleSendMessage} disabled={isLoading || isRestoring} />
    </Card>
  );
}
