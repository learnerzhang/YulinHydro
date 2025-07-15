# routers/document.py
from typing import List
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
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

# 定义搜索请求模型
class SearchQuery(BaseModel):
    query: str
    page_size: int = 10
    page_number: int = 1
    search_in: List[str] = ["fragments.content", "document.content"]  # 指定搜索范围

@router.get("/documents/{document_id}")
async def get_document_detail(document_id: int, db: AsyncSession = Depends(get_db), request: Request = None):
    """
    根据文档ID获取文档详细信息
    
    - 参数: document_id - 文档ID
    - 返回: 文档详细信息，包含标题、描述、内容、标签等
    """
    document = await doc_crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    base_url = "http://127.0.0.1:5000/"
    # 去除file_path中的"static/"前缀，因为静态文件路由通常直接映射到static目录下的内容
    file_url = f"{base_url}{document.file_path}"

    return {
        "status": 200,
        "data": {
            "id": document.id,
            "title": document.title,
            "description": document.description,
            "content": document.content,
            "tag_string": document.tag_string,
            "file_path": document.file_path,
            "file_url": file_url,  # 新增完整URL字段
            "file_type": document.file_type,
            "parsed": document.parsed,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
    }

@router.post("/recreate_es_index")
async def recreate_es_index():
    from app.utils.es_utils import create_index
    try:
        create_index(force_recreate=True)
        return {"message": "ES索引重建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引重建失败: {str(e)}")

@router.post("/es_search_related")
def es_search_related(query: SearchQuery):
    try:
        results = enhanced_search(
            query=query.query,
            search_in=query.search_in,
            page_size=query.page_size,
            page_number=query.page_number
        )
        
        hits = results['hits']['hits']
        processed_results = []
        
        for hit in hits:
            source = hit['_source']
            highlight = hit.get('highlight', {})
            
            # 文档高亮
            doc_highlight = highlight.get('document.content', [])
            
            # 片段高亮
            matched_fragments = []
            if 'inner_hits' in hit and 'fragments' in hit['inner_hits']:
                for frag_hit in hit['inner_hits']['fragments']['hits']['hits']:
                    frag_source = frag_hit['_source']
                    frag_highlight = frag_hit.get('highlight', {})
                    frag_content = frag_highlight.get('fragments.content', [frag_source['content']])[0]
                    
                    matched_fragments.append({
                        "content": frag_source['content'],
                        "page_idx": frag_source['page_idx'],
                        "bbox": frag_source['bbox'],
                        "highlight": frag_content
                    })
            
            processed_results.append({
                "document_id": source['document_id'],
                "document_title": source['document']['title'],
                "document_highlight": doc_highlight[0] if doc_highlight else source['document']['content'][:200] + "...",
                "matched_fragments": matched_fragments,
                "score": hit['_score']
            })
        
        return {
            "total": results['hits']['total']['value'],
            "results": processed_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索处理错误: {str(e)}")
    

@router.get("/default_search")
async def search_documents(query: str = "", db: AsyncSession = Depends(get_db), page_size: int = 10, page_number: int = 1):
    # 计算偏移量
    offset = (page_number - 1) * page_size
    # 执行搜索并获取分页结果
    pagination = await doc_crud.search_documents_with_pagination(db, query, offset, page_size)

    return {
        "status": 200,
        "total": pagination.total,
        "page_size": page_size,
        "page_number": page_number,
        "results": pagination.items
    }

