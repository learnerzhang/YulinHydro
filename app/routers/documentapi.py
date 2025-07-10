# routers/document.py
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import doc_crud, schemas
from app.database import get_db
from app.utils.es_utils import enhanced_search
from pydantic import BaseModel
from datetime import datetime
import hashlib
import os
import uuid

router = APIRouter()

# 索引名称
INDEX_NAME = "pdf_fragments"

# 定义搜索请求模型
class SearchQuery(BaseModel):
    query: str
    page_size: int = 10
    page_number: int = 1


@router.post("/upload-batch")
async def upload_batch_documents(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    uploaded_documents = []
    for file in files:
        # 读取文件内容
        file_content = await file.read()

        # 计算文件内容的哈希值
        file_hash = hashlib.sha256(file_content).hexdigest()

        # 获取文件扩展名
        file_ext = os.path.splitext(file.filename)[1]

        # 构造新的文件名
        file_name = f"{file_hash}{file_ext}"
        # 确保上传目录存在
        upload_dir = "static/documents"
        os.makedirs(upload_dir, exist_ok=True)
        # 构建新的文件路径
        file_path = os.path.join(upload_dir, file_name)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)

        content = f"文件内容提取占位符: {file.filename}"

        document = await doc_crud.create_document(
            db,
            title=file.filename,
            description="",
            content=content,
            tags="",
            file_path=file_path,
            file_type=file_ext[1:]
        )
        uploaded_documents.append(document)

    return uploaded_documents

# 索引名称
INDEX_NAME = "pdf_docs"

# 定义搜索请求模型
class SearchQuery(BaseModel):
    query: str
    page_size: int = 10
    page_number: int = 1
    search_in: List[str] = ["fragments.content", "document.content"]  # 指定搜索范围


@router.post("/es_search_related")
def es_search_related(query: SearchQuery):
    try:
        # 使用ES工具类进行搜索
        results = enhanced_search(
            query=query.query,
            search_in=query.search_in,
            page_size=query.page_size,
            page_number=query.page_number
        )
        
        # 处理搜索结果
        hits = results['hits']['hits']
        processed_results = []
        
        for hit in hits:
            source = hit['_source']
            document_highlight = hit.get('highlight', {}).get('document.content', [])
            
            # 提取匹配的片段
            matched_fragments = []
            if 'inner_hits' in hit and 'fragments' in hit['inner_hits']:
                for fragment_hit in hit['inner_hits']['fragments']['hits']['hits']:
                    fragment = fragment_hit['_source']
                    fragment['highlight'] = fragment_hit.get('highlight', {}).get('fragments.content', [fragment['content']])[0]
                    matched_fragments.append(fragment)
            
            processed_results.append({
                "document_id": source['document_id'],
                "document_title": source['document']['title'],
                "document_highlight": document_highlight[0] if document_highlight else source['document']['content'][:200] + "...",
                "matched_fragments": matched_fragments,
                "score": hit['_score']
            })
        
        return {
            "total": results['hits']['total']['value'],
            "results": processed_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/search")
async def search_documents(query: str="", db: AsyncSession = Depends(get_db), page_size: int = 10, page_number: int = 1):
    return await doc_crud.search_documents(db, query, page_number, page_size)