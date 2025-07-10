# 导入 AsyncSession
from app.dbmodels import Tag
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app import schemas, doc_crud
from app.database import get_db
from sqlalchemy import func, select

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "未找到"}}
)

# 所有路由函数的 db 参数注解改为 AsyncSession
@router.get("/", response_model=dict)
async def get_tags(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):  # 这里修改
    tags = await doc_crud.get_tags(db, skip=skip, limit=limit)
    # 返回获取到的标签
    return {"data": tags, "total": len(tags)}

@router.post("/", response_model=schemas.Tag)
async def create_tag(tag: schemas.TagCreate, db: AsyncSession = Depends(get_db)):  # 这里修改
    db_tag = await doc_crud.get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=400, detail="标签已存在")
    return await doc_crud.create_tag(db=db, tag=tag)

@router.get("/{tag_id}", response_model=schemas.Tag)
async def get_tag(tag_id: int, db: AsyncSession = Depends(get_db)):  # 这里修改
    db_tag = await doc_crud.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签未找到")
    return db_tag

@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int, 
    db: AsyncSession = Depends(get_db)  # 同样注解为AsyncSession
):
    db_tag = await doc_crud.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签未找到")
    await doc_crud.delete_tag(db, tag_id=tag_id)
    return {"message": "标签删除成功"}