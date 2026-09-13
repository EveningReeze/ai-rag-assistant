# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DeepSeek 配置（Chat 用）
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    chat_model: str = "deepseek-chat"

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "ai-doc-assistant"
    pinecone_environment: str = "us-east-1"

    # 本地 Embedding 模型
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dimension: int = 512   # bge-small-zh-v1.5 的维度

    # 切片参数
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()