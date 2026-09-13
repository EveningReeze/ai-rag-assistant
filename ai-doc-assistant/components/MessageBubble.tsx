// src/components/MessageBubble.tsx
import { Message } from '@/types';
import { Bot, User, Quote } from 'lucide-react';

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 p-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-blue-600' : 'bg-emerald-600'
      }`}>
        {isUser ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
      </div>

      {/* 消息内容 */}
      <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
        isUser ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm'
      }`}>
        <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
        
        {/* 渲染引用来源 */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
              <Quote className="w-3 h-3" /> 引用来源:
            </p>
            <div className="flex flex-wrap gap-2">
              {message.citations.map((cite, idx) => (
                <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md border border-gray-200">
                  {cite}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}