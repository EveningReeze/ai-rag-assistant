# backend/app/services/document.py
import os
from pypdf import PdfReader
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 提取文本"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """从 Word 提取文本"""
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text])

def extract_text(file_path: str) -> str:
    """根据文件后缀选择解析器"""
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_path}")

def chunk_text(text: str) -> list[str]:
    """将文本切分成块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )
    return splitter.split_text(text)