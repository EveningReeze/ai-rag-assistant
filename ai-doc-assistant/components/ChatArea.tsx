// src/components/ChatArea.tsx
'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/types';
import MessageBubble from './MessageBubble';
import { Bot } from 'lucide-react';

export default function ChatArea({ messages, isLoading }: { messages: Message[], isLoading: boolean }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50/50">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-gray-400">
          <Bot className="w-16 h-16 mb-4 text-gray-300" />
          <p className="text-lg">你好！我是你的智能文档助手。</p>
          <p className="text-sm">请在左侧上传文档，然后向我提问。</p>
        </div>
      ) : (
        <div className="max-w-4xl mx-auto py-6">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          
          {/* 加载状态 */}
          {isLoading && (
            <div className="flex gap-4 p-4">
              <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}