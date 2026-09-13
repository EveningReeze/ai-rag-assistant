// src/lib/api.ts
import axios from 'axios';
import { Message } from '@/types';

// 假设 FastAPI 运行在 8000 端口
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const api = {
  // 上传文档
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // 发送问题并获取回答
  sendMessage: async (question: string): Promise<Message> => {
    const response = await apiClient.post('/chat', { question });
    // 假设后端返回格式: { answer: "...", citations: ["doc1.pdf"] }
    return {
      id: Date.now().toString(),
      role: 'assistant',
      content: response.data.answer,
      citations: response.data.citations,
    };
  },
};