// src/types/index.ts

// 消息类型
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: string[]; // AI 回答附带的引用来源
}

// 文档类型
export interface DocumentItem {
  id: string;
  name: string;
  status: 'processing' | 'ready' | 'error';
  uploadTime: string;
}