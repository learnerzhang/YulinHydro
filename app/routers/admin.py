from app.utils import utils
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app import base_crud, dbmodels, schemas
from app.database import get_db
from app.routers.auth import get_current_active_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# 验证管理员权限
async def get_current_admin_user(current_user: dbmodels.User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# 新接口：返回首页所需数据
@router.get("/homepage-data", response_model=schemas.HomepageData)
async def get_homepage_data(
    db: AsyncSession = Depends(get_db),
):
    # 获取总用户数
    stmt_total_users = select(func.count()).select_from(dbmodels.User)
    result_total_users = await db.execute(stmt_total_users)
    total_users = result_total_users.scalar()

    # 获取今日签到人数，去重处理
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    stmt_today_attendance = select(func.count(func.distinct(dbmodels.AttendanceRecord.user_id))).select_from(dbmodels.AttendanceRecord).where(
        dbmodels.AttendanceRecord.timestamp >= today,
        dbmodels.AttendanceRecord.timestamp < tomorrow
    )
    result_today_attendance = await db.execute(stmt_today_attendance)
    today_attendance = result_today_attendance.scalar()

    # 计算签到率
    attendance_rate = (today_attendance / total_users) * 100 if total_users > 0 else 0

    # 获取最近一个月的签到人数，去重处理
    one_month_ago = datetime.now() - timedelta(days=29)
    dates = []
    counts = []
    for i in range(30):
        current_date = one_month_ago + timedelta(days=i)
        next_date = current_date + timedelta(days=1)
        stmt_daily_attendance = select(func.count(func.distinct(dbmodels.AttendanceRecord.user_id))).select_from(dbmodels.AttendanceRecord).where(
            dbmodels.AttendanceRecord.timestamp >= current_date,
            dbmodels.AttendanceRecord.timestamp < next_date
        )
        result_daily_attendance = await db.execute(stmt_daily_attendance)
        daily_attendance = result_daily_attendance.scalar()
        dates.append(f"{current_date.month}/{current_date.day}")
        counts.append(daily_attendance)

    return {
        "total_users": total_users,
        "today_attendance": today_attendance,
        "attendance_rate": attendance_rate,
        "dates": dates,
        "counts": counts
    }

# 获取所有用户
@router.get("/users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    users = base_crud.get_users(db, skip=skip, limit=limit)
    return users
from app.schemas import AttendanceRecord as AttendanceRecordSchema
# 获取所有签到记录，支持多条件查询和分页
# 修改路由定义
@router.get("/attendance-records", response_model=schemas.PagedResponse[schemas.AttendanceRecord])
async def get_all_attendance_records(
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    records = await base_crud.get_attendance_records(
        db, skip=skip, limit=limit, start_date=start_date, end_date=end_date, user_id=user_id
    )
    
    # 将 ORM 对象转换为 Pydantic 模型
    items = [schemas.AttendanceRecord.from_orm(record) for record in records]
    
    # 使用异步方式查询总数
    stmt = select(func.count()).select_from(dbmodels.AttendanceRecord)
    result = await db.execute(stmt)
    total = result.scalar()
    
    return {
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "items": items  # 使用转换后的模型
    }

# 删除签到记录
@router.delete("/attendance-records/{record_id}", response_model=schemas.AttendanceRecord)
async def delete_attendance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    record = await base_crud.get_attendance_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(record)
    db.commit()
    return record

# 获取所有用户
@router.get("/users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    users = base_crud.get_users(db, skip=skip, limit=limit)
    return users

# 创建用户（管理员）
@router.post("/users", response_model=schemas.User)
async def create_user_by_admin(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),  # 使用 AsyncSession
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    db_user = await base_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已注册")
    
    db_user = await base_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    return await base_crud.create_user(db=db, user=user)


# 更新签到记录状态
@router.put("/attendance-records/{record_id}", response_model=schemas.AttendanceRecord)
async def update_attendance_record_status(
    record_id: int,
    is_verified: bool,
    db: Session = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_admin_user)
):
    record = base_crud.get_attendance_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    updated_record = base_crud.update_attendance_record(db, record_id, is_verified)
    return updated_record
    