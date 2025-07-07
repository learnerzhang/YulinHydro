import os
from app.es_utils import index_document
from sqlalchemy.orm import Session
from app import dbmodels, schemas
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

# 新增文档操作
async def create_document(
    db: AsyncSession, 
    title: str, 
    description: str, 
    content: str,
    tags: str,
    file_path: str,
    file_type: str
):
    db_document = dbmodels.Document(
        title=title,
        description=description,
        content=content,
        tags=tags,
        file_path=file_path,
        file_type=file_type
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document

async def update_document(db: AsyncSession, doc_id: int, **kwargs):
    document = await db.get(dbmodels.Document, doc_id)
    if document:
        for key, value in kwargs.items():
            setattr(document, key, value)
        document.updated_at = datetime.now()
        await db.commit()
        await db.refresh(document)
        
        # 更新ES索引
        index_document(
            document.id,
            document.title,
            document.description,
            document.content,
            document.tags,
            document.file_path
        )
    return document

async def delete_document(db: AsyncSession, doc_id: int):
    document = await db.get(dbmodels.Document, doc_id)
    if document:
        await db.delete(document)
        await db.commit()
        # 删除ES索引
        delete_document(doc_id)
        # 删除物理文件
        try:
            os.remove(document.file_path)
        except OSError:
            pass
    return document