# backend/app/services/chat.py
import json
from openai import OpenAI
from app.config import settings
from app.services.vector import search_similar

# 用 DeepSeek 的 base_url 初始化 client
client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url,
)

SYSTEM_PROMPT = """你是一个专业的智能文档问答助手。请严格遵守以下规则：

1. 只根据用户提供的【上下文】来回答问题，不要编造任何信息。
2. 如果【上下文】中没有相关信息，请回答："根据提供的文档，我无法回答这个问题"，并将 citations 设为空数组。
3. 必须严格以 JSON 格式输出，不要包含任何其他文字或 Markdown 标记。

输出 JSON 格式：
{
    "answer": "你的回答内容（中文）",
    "citations": ["来源文档名称1", "来源文档名称2"]
}
"""


def build_user_prompt(question: str, contexts: list[dict]) -> str:
    context_text = "\n\n---\n\n".join(
        f"【来源：{c['doc_name']}】\n{c['text']}" for c in contexts
    )
    return f"【上下文】\n{context_text}\n\n【用户问题】\n{question}"


def call_llm_with_retry(user_prompt: str, max_retries: int = 2) -> dict:
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=settings.chat_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )

            raw_content = response.choices[0].message.content or ""
            result = json.loads(raw_content)

            if "answer" not in result or not isinstance(result["answer"], str):
                raise ValueError("返回 JSON 缺少合法的 answer 字段")

            if "citations" not in result or not isinstance(result["citations"], list):
                result["citations"] = []

            return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            print(f"[Attempt {attempt + 1}] LLM 返回格式错误: {e}")

    return {
        "answer": f"抱歉，模型返回格式异常，请稍后重试。({last_error})",
        "citations": [],
    }


def rag_query(question: str) -> dict:
    contexts = search_similar(question)

    if not contexts:
        return {
            "answer": "知识库中暂无相关文档，请先上传文档后再提问。",
            "citations": [],
        }

    user_prompt = build_user_prompt(question, contexts)
    return call_llm_with_retry(user_prompt)