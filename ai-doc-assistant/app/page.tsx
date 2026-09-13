// src/app/page.tsx
'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import ChatInput from '@/components/ChatInput';
import { Message } from '@/types';
import { api } from '@/lib/api';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    // 1. 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 2. 调用后端 API 获取回答
      const aiMessage = await api.sendMessage(content);
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      // 错误处理
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: '抱歉，处理您的请求时出现了错误，请稍后重试。',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* 左侧：文档管理 */}
      <Sidebar />
      
      {/* 右侧：对话区域 */}
      <div className="flex-1 flex flex-col h-full relative">
        <header className="h-14 border-b border-gray-200 flex items-center px-6 bg-white/80 backdrop-blur-sm z-10">
          <h1 className="text-lg font-semibold text-gray-800">AI 智能文档问答助手</h1>
        </header>
        
        <ChatArea messages={messages} isLoading={isLoading} />
        
        <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}