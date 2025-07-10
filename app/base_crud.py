import os
from sqlalchemy.orm import Session
from app import dbmodels, schemas
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

# 用户操作
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(dbmodels.User).where(dbmodels.User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(dbmodels.User).where(dbmodels.User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user(db: AsyncSession, user_id: int):
    stmt = select(dbmodels.User).where(dbmodels.User.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(dbmodels.User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 将同步函数改为异步
async def create_user(db: AsyncSession, user: schemas.UserCreate, face_encoding: Optional[bytes] = None):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = dbmodels.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=fake_hashed_password,
        face_encoding=face_encoding
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

def update_user_face_encoding(db: Session, user_id: int, face_encoding: bytes):
    user = db.query(dbmodels.User).filter(dbmodels.User.id == user_id).first()
    if user:
        user.face_encoding = face_encoding
        db.commit()
        db.refresh(user)
    return user

# 签到记录操作
async def create_attendance_record(db: AsyncSession, record: schemas.AttendanceRecordCreate):
    db_record = dbmodels.AttendanceRecord(
        user_id=record.user_id,
        photo_path=record.photo_path,
        is_verified=record.is_verified
    )
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

# 签到记录操作
async def get_attendance_records_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    stmt = select(dbmodels.AttendanceRecord).where(dbmodels.AttendanceRecord.user_id == user_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
from sqlalchemy.orm import joinedload
async def get_attendance_records(
    db: AsyncSession, skip: int = 0, limit: int = 100, 
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, 
    user_id: Optional[int] = None
):
    stmt = select(dbmodels.AttendanceRecord).options(joinedload(dbmodels.AttendanceRecord.user))
    
    if start_date:
        stmt = stmt.where(dbmodels.AttendanceRecord.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(dbmodels.AttendanceRecord.timestamp <= end_date)
    if user_id:
        stmt = stmt.where(dbmodels.AttendanceRecord.user_id == user_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_attendance_record(db: AsyncSession, record_id: int):
    stmt = select(dbmodels.AttendanceRecord).where(dbmodels.AttendanceRecord.id == record_id)
    result = await db.execute(stmt)
    return result.scalars().first()

def update_attendance_record(db: Session, record_id: int, is_verified: Optional[bool] = None):
    record = db.query(dbmodels.AttendanceRecord).filter(dbmodels.AttendanceRecord.id == record_id).first()
    if record and is_verified is not None:
        record.is_verified = is_verified
        db.commit()
        db.refresh(record)
    return record

async def get_attendance_records_count_by_user(db: AsyncSession, user_id: int):
    stmt = select(func.count(dbmodels.AttendanceRecord.id)).where(dbmodels.AttendanceRecord.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar()


async def delete_attendance_record(db: AsyncSession, record_id: int):
    # 使用异步查询方法
    stmt = select(dbmodels.AttendanceRecord).where(dbmodels.AttendanceRecord.id == record_id)
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if record:
        await db.delete(record)
        await db.commit()
    return record
