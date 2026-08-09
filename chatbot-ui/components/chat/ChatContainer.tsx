'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTheme } from 'next-themes';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Message } from '@/types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Moon, Sun, Loader2, LogOut, User, Plus } from 'lucide-react';
import RuixenMoonChat from '@/components/ui/ruixen-moon-chat';

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

    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      currentToken = token;
      setAuthToken(token);
      const user = await getAuthenticatedCustomer(token);
      if (user) {
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
        localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
        conversationIdRef.current = null;
      }
    }

    const sessionInfo = await fetchSessionConversation(sessionId, currentToken);
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

  const resetAuthForm = useCallback(() => {
    setEmailInput('');
    setPasswordInput('');
    setNameInput('');
    setAuthError('');
  }, []);

  const handleOpenAuthModal = (mode: 'login' | 'register' = 'login') => {
    resetAuthForm();
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  const handleCloseAuthModal = () => {
    setShowAuthModal(false);
    resetAuthForm();
  };

  const handleSwitchAuthMode = (mode: 'login' | 'register') => {
    resetAuthForm();
    setAuthMode(mode);
  };

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
      resetAuthForm();

      localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
      conversationIdRef.current = null;
      const newSessionId = crypto.randomUUID();
      localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);
      sessionIdRef.current = newSessionId;
      setMessages([]);
      restoredRef.current = false;
      setIsRestoring(true);
      restoreSession();
    } catch (err: any) {
      const errMsg = typeof err === 'string'
        ? err
        : typeof err?.message === 'string'
          ? err.message
          : 'Authentication failed. Invalid email or password.';
      setAuthError(errMsg);
    }

  };

  const handleLogout = async () => {
    await logoutCustomer(authToken);
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID);
    const newSessionId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);
    sessionIdRef.current = newSessionId;
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

  const isLandingState = messages.length === 0 && !isRestoring;

  return (
    <div className="w-full h-full flex flex-col relative overflow-hidden bg-aurora-canvas text-zinc-100 font-sans">
      {/* Unified Screen Canvas Background Layers */}
      <div className="bg-cyber-grid" />
      <div className="bg-glow-orb-1" />
      <div className="bg-glow-orb-2" />
      <div className="aurora-layer-1" />
      <div className="aurora-light-sweep" />
      <div className="noise-overlay" />

      {/* Seamless Glass Top Header Navbar */}
      <header className="px-6 py-3.5 border-b border-zinc-800/40 bg-[#08080a]/70 backdrop-blur-md flex items-center justify-between z-30 shrink-0">




        <div>
          <h2 className="text-base font-sharp-heading text-white tracking-tight flex items-center gap-2">
            SupportFlow AI
          </h2>

          <p className="text-[11px] text-zinc-400">
            {authUser ? (
              <span className="text-zinc-300 font-medium">
                Logged in as {authUser.name || authUser.email}
              </span>
            ) : (
              <span>Guest Session • Sign in for account options</span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleNewChat}
              className="bg-zinc-900 border-zinc-800 hover:bg-zinc-800 text-zinc-200 text-xs gap-1 h-8 rounded-xl"
            >
              <Plus className="h-3.5 w-3.5" />
              New Chat
            </Button>
          )}

          {authUser ? (
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="bg-zinc-900 border-zinc-800 hover:bg-zinc-800 text-zinc-200 text-xs gap-1.5 h-8 rounded-xl"
            >
              <LogOut className="h-3.5 w-3.5" />
              Logout
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={() => handleOpenAuthModal('login')}
              className="bg-white hover:bg-zinc-200 text-zinc-950 font-medium text-xs gap-1.5 h-8 rounded-xl shadow-md"
            >
              <User className="h-3.5 w-3.5" />
              Sign In
            </Button>
          )}
        </div>
      </header>

      {/* Auth Modal Overlay */}
      {showAuthModal && (
        <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 bg-zinc-900 border-zinc-800 text-white shadow-2xl rounded-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-semibold text-zinc-200">
                {authMode === 'login' ? 'Customer Login' : 'Create Customer Account'}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCloseAuthModal}
                className="text-zinc-400 hover:text-white"
              >
                ✕
              </Button>
            </div>

            {authError && (
              <div className="mb-4 p-2.5 text-xs bg-red-950/80 border border-red-500/40 text-red-300 rounded-lg">
                {authError}
              </div>
            )}

            <form onSubmit={handleAuthSubmit} className="space-y-4">
              {authMode === 'register' && (
                <div>
                  <label className="text-xs font-medium block mb-1 text-zinc-300">Full Name</label>
                  <Input
                    type="text"
                    placeholder="Alice Johnson"
                    value={nameInput}
                    onChange={(e) => setNameInput(e.target.value)}
                    autoComplete="name"
                    className="bg-zinc-950 border-zinc-800 text-white placeholder:text-zinc-500"
                  />
                </div>
              )}

              <div>
                <label className="text-xs font-medium block mb-1 text-zinc-300">Email Address</label>
                <Input
                  type="email"
                  required
                  placeholder="alice.johnson@example.com"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  autoComplete="email"
                  className="bg-zinc-950 border-zinc-800 text-white placeholder:text-zinc-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium block mb-1 text-zinc-300">Password</label>
                <Input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                  className="bg-zinc-950 border-zinc-800 text-white placeholder:text-zinc-500"
                />
              </div>

              <Button type="submit" className="w-full bg-white hover:bg-zinc-200 text-zinc-950 font-medium">
                {authMode === 'login' ? 'Sign In' : 'Register Account'}
              </Button>
            </form>

            <div className="mt-4 text-center text-xs text-zinc-400">
              {authMode === 'login' ? (
                <span>
                  Don't have an account?{' '}
                  <button
                    className="text-zinc-200 underline font-medium hover:text-white ml-1"
                    onClick={() => handleSwitchAuthMode('register')}
                  >
                    Register
                  </button>
                </span>
              ) : (
                <span>
                  Already have an account?{' '}
                  <button
                    className="text-zinc-200 underline font-medium hover:text-white ml-1"
                    onClick={() => handleSwitchAuthMode('login')}
                  >
                    Sign In
                  </button>
                </span>
              )}
            </div>
          </Card>
        </div>
      )}


      {/* Main Content Area */}
      <div className="flex-1 relative overflow-hidden flex flex-col z-10">
        {isRestoring ? (
          <div className="h-full flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
          </div>
        ) : isLandingState ? (
          /* Initial SupportFlow AI Landing Hero State */
          <div className="flex-1 w-full h-full relative overflow-hidden">
            <RuixenMoonChat
              onSendMessage={handleSendMessage}
              disabled={isLoading || isRestoring}
            />
          </div>
        ) : (
          /* Active Conversation State */
          <div className="w-full h-full min-h-0 flex flex-col overflow-hidden relative">
            <div className="flex-1 min-h-0 w-full overflow-hidden flex flex-col">
              <MessageList messages={messages} isLoading={isLoading} />
            </div>

            <div className="p-3 sm:p-4 bg-gradient-to-t from-zinc-950 via-zinc-950/90 to-transparent shrink-0 w-full z-20">


              <div className="max-w-5xl mx-auto w-full">
                <MessageInput
                  onSendMessage={handleSendMessage}
                  disabled={isLoading || isRestoring}
                  placeholder="Type your request..."
                />
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}


