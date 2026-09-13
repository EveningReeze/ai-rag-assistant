# backend/app/services/vector.py
import uuid
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from app.config import settings

# ---- 初始化向量模型（本地） ----
# 第一次运行会下载约 100MB 的模型文件，缓存在本地
print(f"[Vector] Loading embedding model: {settings.embedding_model}")
embedding_model = SentenceTransformer(settings.embedding_model)
print("[Vector] Embedding model loaded.")

# ---- 初始化 Pinecone ----
pc = Pinecone(api_key=settings.pinecone_api_key)


def get_or_create_index():
    existing = [idx.name for idx in pc.list_indexes()]
    print(f"[Vector] Existing indexes: {existing}")
    
    if settings.pinecone_index_name not in existing:
        print(f"[Vector] Creating index {settings.pinecone_index_name} (dim={settings.embedding_dimension})")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.pinecone_environment,
            ),
        )
    else:
        print(f"[Vector] Reusing existing index {settings.pinecone_index_name}")
    
    return pc.Index(settings.pinecone_index_name)
index = get_or_create_index()


def get_embedding(text: str) -> list[float]:
    """用本地模型生成向量"""
    # normalize_embeddings=True 提升余弦相似度效果
    vector = embedding_model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def upsert_chunks(chunks: list[str], doc_id: str, doc_name: str) -> None:
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        vectors.append({
            # ⭐ ID 必须是纯 ASCII，所以只用 doc_id + 序号
            "id": f"{doc_id}_chunk_{i}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "doc_id": doc_id,
                # 中文文件名放在 metadata 里，不受 ASCII 限制
                "doc_name": doc_name,
                "chunk_index": i,
            },
        })

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i + batch_size])

def search_similar(query: str, top_k: int | None = None) -> list[dict]:
    top_k = top_k or settings.top_k
    query_embedding = get_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    return [
        {
            "text": match.metadata.get("text", ""),
            "doc_name": match.metadata.get("doc_name", "未知文档"),
            "score": match.score,
        }
        for match in results.matches
    ]


def generate_doc_id(filename: str) -> str:
    """生成纯 ASCII 的 doc_id，避免中文导致 Pinecone 报错"""
    return uuid.uuid4().hex[:8]