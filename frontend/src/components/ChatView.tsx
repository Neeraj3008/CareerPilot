import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Sparkles, Bot, User, Wrench, 
  CornerDownLeft, RefreshCw, CheckCircle2 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ChatMessage, ToolCallExecution } from '../types';

export const ChatView: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hello! I am your CareerPilot AI Advisor. I can search jobs, analyze your resume skills, calculate deterministic recommendation scores, and update your career preferences. How can I help you today?",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await api.chat.send(text, conversationId);
      setConversationId(res.conversation_id);

      const asstMsg: ChatMessage = {
        role: 'assistant',
        content: res.reply,
        tool_calls: res.tool_calls_executed,
      };
      setMessages(prev => [...prev, asstMsg]);
    } catch (err: any) {
      console.error('Chat error', err);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an issue executing your request. Please ensure you are logged in and try again.',
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    "What are my top recommended jobs?",
    "Find remote AI and machine learning roles",
    "Show my candidate profile summary",
    "Which skills are missing from my resume for senior roles?"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-h-[850px] bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-slate-900">CareerPilot Autonomous Agent</h2>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">
              Native tool calling with genuine database execution & RAG
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            setMessages([{
              role: 'assistant',
              content: "Session reset. How can I assist your career search?",
            }]);
            setConversationId(undefined);
          }}
          className="text-xs text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          title="Reset Chat Session"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Pane */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          return (
            <div key={index} className={`flex space-x-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="w-8 h-8 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-2xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Tool Call Badges */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="space-y-1.5 mb-2">
                    {msg.tool_calls.map((tc, tIdx) => (
                      <div 
                        key={tIdx} 
                        className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-semibold"
                      >
                        <Wrench className="w-3 h-3 text-indigo-500" />
                        <span>Executed Tool:</span>
                        <code className="bg-indigo-100 px-1 rounded text-indigo-900">{tc.tool}()</code>
                      </div>
                    ))}
                  </div>
                )}

                <div
                  className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? 'bg-brand-600 text-white rounded-tr-none shadow-sm'
                      : 'bg-slate-100/80 text-slate-800 rounded-tl-none border border-slate-200/50'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.content}</p>
                </div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center flex-shrink-0 mt-0.5 font-bold text-xs">
                  {user ? user.full_name[0].toUpperCase() : 'U'}
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div className="flex space-x-3 justify-start items-center">
            <div className="w-8 h-8 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3.5 rounded-2xl bg-slate-100 border border-slate-200 flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce"></div>
              <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce [animation-delay:0.2s]"></div>
              <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce [animation-delay:0.4s]"></div>
              <span className="text-xs text-slate-500 font-medium ml-2">Calling tools & computing recommendations...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Pills */}
      {messages.length <= 2 && (
        <div className="px-6 py-2 border-t border-slate-100 bg-slate-50/50 flex flex-wrap gap-2">
          {samplePrompts.map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="text-xs bg-white hover:bg-brand-50 hover:text-brand-700 text-slate-600 font-medium px-3 py-1.5 rounded-full border border-slate-200 transition-colors shadow-2xs"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <div className="p-4 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything (e.g. 'Recommend jobs', 'What are my top skills?', 'Search remote roles')..."
            className="w-full pl-4 pr-12 py-3 rounded-xl border border-slate-200 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="absolute right-2 p-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40 transition-colors shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
