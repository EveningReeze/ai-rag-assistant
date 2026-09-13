// src/components/Sidebar.tsx
'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { DocumentItem } from '@/types';
import { api } from '@/lib/api';

export default function Sidebar() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const newDoc: DocumentItem = {
        id: Date.now().toString() + file.name,
        name: file.name,
        status: 'processing',
        uploadTime: new Date().toLocaleTimeString(),
      };
      
      setDocuments((prev) => [newDoc, ...prev]);

      try {
        // 调用后端上传接口
        await api.uploadDocument(file);
        setDocuments((prev) =>
          prev.map((doc) => (doc.id === newDoc.id ? { ...doc, status: 'ready' } : doc))
        );
      } catch (error) {
        console.error('Upload failed:', error);
        setDocuments((prev) =>
          prev.map((doc) => (doc.id === newDoc.id ? { ...doc, status: 'error' } : doc))
        );
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">知识库管理</h2>
        
        {/* 上传区域 */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
          }`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto h-8 w-8 text-gray-400 mb-2" />
          <p className="text-sm text-gray-600">拖拽 PDF/Word 到此处，或点击上传</p>
        </div>
      </div>

      {/* 文档列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {documents.map((doc) => (
          <div key={doc.id} className="flex items-center gap-3 p-3 bg-white rounded-lg shadow-sm border border-gray-100">
            <FileText className="h-5 w-5 text-blue-500 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{doc.name}</p>
              <p className="text-xs text-gray-400">{doc.uploadTime}</p>
            </div>
            {doc.status === 'processing' && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
            {doc.status === 'ready' && <CheckCircle className="h-4 w-4 text-green-500" />}
            {doc.status === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
          </div>
        ))}
        {documents.length === 0 && (
          <p className="text-sm text-gray-400 text-center mt-10">暂无文档，请先上传</p>
        )}
      </div>
    </div>
  );
}