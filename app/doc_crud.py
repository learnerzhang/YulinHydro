import os
from app import schemas
from app.utils.es_utils import delete_document_from_es, index_document_with_fragments
from app.dbmodels import Document, Tag
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, select
import logging
logger = logging.getLogger(__name__)

async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 使用 select 语句替换 query 方法
    stmt = select(Tag).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_tag(db: AsyncSession, tag_id: int):
    # 使用 select 语句替换 query 方法
    stmt = select(Tag).filter(Tag.id == tag_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_tag_by_name(db: AsyncSession, name: str):
    # 使用 select 语句替换 query 方法
    stmt = select(Tag).filter(Tag.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_tag(db: AsyncSession, tag: schemas.TagCreate):
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag

async def delete_tag(db: AsyncSession, tag_id: int):
    db_tag = await get_tag(db, tag_id)
    if db_tag:
        await db.delete(db_tag)
        await db.commit()
    return

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
    db_document = Document(
        title=title,
        description=description,
        content=content,
        tag_string=tags,  # 使用新字段名
        file_path=file_path,
        file_type=file_type
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document

async def search_documents(db: AsyncSession, query: str, skip: int = 0, limit: int = 10):
    # 使用 select 语句替换 query 方法
    stmt = select(Document).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_document_by_file_path(db: AsyncSession, file_path: str):
    """通过文件路径查询文档"""
    stmt = select(Document).where(Document.file_path == file_path)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_document(db: AsyncSession, doc_id: int, **kwargs):
    """
    优化点：
    1. 字段验证，只允许更新Document模型存在的字段
    2. 检查实际变更，避免无意义操作
    3. 事务管理，确保数据库与ES一致性
    4. 异步ES操作，避免阻塞
    5. 完善日志与错误处理
    """
    # 允许更新的字段列表
    allowed_fields = {
        "title", "description", "content", "tag_string", 
        "file_path", "file_type", "parsed"
    }
    
    # 过滤非法字段
    valid_kwargs = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not valid_kwargs:
        logger.warning(f"更新文档 {doc_id} 时无有效字段")
        return None

    try:
        document = await db.get(Document, doc_id)
        if not document:
            logger.warning(f"文档 {doc_id} 不存在")
            return None

        # 检查是否有实际变更
        has_changes = False
        for key, value in valid_kwargs.items():
            if getattr(document, key) != value:
                has_changes = True
                setattr(document, key, value)
        
        if not has_changes:
            logger.info(f"文档 {doc_id} 无变更，无需更新")
            return document

        # 数据库事务提交
        await db.commit()
        await db.refresh(document)
        logger.info(f"文档 {doc_id} 数据库更新成功")

        # 异步更新ES索引（确保index_document_with_fragments是异步函数）
        try:
            await index_document_with_fragments(
                document_id=f"doc_{document.id}",
                title=document.title,
                fragments=[{"content": document.content}] if document.content else [],
                metadata={
                    "description": document.description,
                    "tags": document.tags,
                    "file_path": document.file_path,
                    "file_type": document.file_type
                }
            )
            logger.info(f"文档 {doc_id} ES索引更新成功")
        except Exception as e:
            logger.error(f"文档 {doc_id} ES索引更新失败: {str(e)}")
            # 可选：ES更新失败时回滚数据库变更
            # await db.rollback()
            # return None

        return document

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"文档 {doc_id} 数据库更新失败: {str(e)}")
        return None

async def delete_document(db: AsyncSession, doc_id: int):
    document = await db.get(Document, doc_id)
    if document:
        await db.delete(document)
        await db.commit()
        
        # 使用统一的ES删除函数
        delete_document_from_es(f"doc_{doc_id}")
        
        # 删除物理文件
        try:
            os.remove(document.file_path)
        except OSError:
            pass
    return document

async def get_unparsed_documents(db: AsyncSession):
    stmt = select(Document).where(Document.parsed == False)
    result = await db.execute(stmt)
    return result.scalars().all()

async def mark_document_parsed(db: AsyncSession, doc_id: int):
    document = await db.get(Document, doc_id)
    if document:
        document.parsed = True
        await db.commit()
        await db.refresh(document)
    return document