# backend/app/main.py
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ChatRequest, ChatResponse, UploadResponse
from app.services import document, vector, chat

app = FastAPI(
    title="AI 智能文档问答助手 API",
    description="基于 FastAPI + OpenAI + Pinecone 的 RAG 后端服务",
    version="1.0.0",
)

# CORS 配置：允许前端 (localhost:3000) 访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://47.82.1.82:3000",       # ⭐ 服务器公网 IP
        "http://localhost:3000",         # 本地开发
        "http://127.0.0.1:3000",         # 本地开发
    ],
    allow_credentials=False,             # ⭐ 必须 False（和通配符不冲突）
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

@app.get("/")
def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "AI Doc Assistant API"}


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档 -> 解析 -> 切片 -> 向量化 -> 存入 Pinecone
    """
    # 1. 校验文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"仅支持 PDF 和 Word 文件，收到: {ext}")

    # 2. 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 3. 提取文本
        print(f"\n[Upload] 开始处理文件: {file.filename}")
        text = document.extract_text(tmp_path)
        print(f"[Upload] 文本提取完成，长度: {len(text)} 字符")

        if not text.strip():
            raise HTTPException(status_code=400, detail="文档内容为空或无法解析")

        # 4. 切片
        chunks = document.chunk_text(text)
        print(f"[Upload] 切片完成，共 {len(chunks)} 个 chunk")

        if not chunks:
            raise HTTPException(status_code=400, detail="文档切片失败")

        # 5. 向量化并存储
        doc_id = vector.generate_doc_id(file.filename or "unknown")
        print(f"[Upload] 开始向量化，doc_id={doc_id}")

        vector.upsert_chunks(chunks, doc_id, file.filename or "unknown")
        print(f"[Upload] 向量化完成，已写入 Pinecone")

        return UploadResponse(
            status="success",
            message=f"文档 {file.filename} 已成功处理并存入知识库",
            doc_id=doc_id,
            chunks_count=len(chunks),
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("\n" + "=" * 70)
        print("[Upload Error] 完整堆栈:")
        traceback.print_exc()
        print("=" * 70 + "\n")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {type(e).__name__}: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    接收用户问题 -> RAG 检索 -> LLM 生成带引用的回答
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        result = chat.rag_query(request.question)
        return ChatResponse(
            answer=result["answer"],
            citations=result.get("citations", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")