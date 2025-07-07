# routers/document.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import doc_crud, schemas
from app.database import get_db
from app.es_utils import index_document, delete_document, search_documents
import os
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = "未命名文档",
    description: str = "",
    tags: str = "",
    db: AsyncSession = Depends(get_db)
):
    # 保存文件
    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join("static/documents", file_name)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 提取文本内容（实际项目需根据文件类型实现）
    content = f"文件内容提取占位符: {title}"
    
    # 创建数据库记录
    document = await doc_crud.create_document(
        db, 
        title=title,
        description=description,
        content=content,
        tags=tags,
        file_path=file_path,
        file_type=file_ext[1:]
    )
    
    # 创建ES索引
    index_document(
        document.id,
        title,
        description,
        content,
        tags,
        file_path
    )
    
    return document

@router.get("/search")
async def search_docs(query: str, page: int = 1, size: int = 10):
    results = search_documents(query, page, size)
    return {
        "total": results["hits"]["total"]["value"],
        "page": page,
        "size": size,
        "results": [hit["_source"] for hit in results["hits"]["hits"]]
    }