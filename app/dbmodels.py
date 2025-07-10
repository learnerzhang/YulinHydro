from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    username = Column(String, unique=True, index=True)
    
    full_name = Column(String)
    
    hashed_password = Column(String)
    
    is_active = Column(Boolean, default=True)
    
    is_admin = Column(Boolean, default=False)
    
    email = Column(String, unique=False, index=True, default='zhangsan@163.com')
    
    phone_number = Column(String, unique=False, index=True, default='13800138000')

    photo_path = Column(String)  # 照片路径
    
    face_encoding = Column(LargeBinary, nullable=True)  # 人脸特征编码
    
    face_encoding_updated_at = Column(DateTime(timezone=True), nullable=True)  # 人脸特征编码更新时间
    
    avatar_path = Column(String, default='static/default.jpg')  # 头像路径
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    attendance_records = relationship("AttendanceRecord", back_populates="user")


    def __str__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
    
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    photo_path = Column(String)  # 签到照片路径
    is_verified = Column(Boolean, default=False)  # 人脸验证状态
    
    user = relationship("User", back_populates="attendance_records")    


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    documents = relationship("Document", secondary="document_tags", back_populates="tags")


class DocumentTag(Base):
    __tablename__ = "document_tags"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))


class Document(AsyncAttrs, Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    content = Column(Text)
    # 修改字段名避免冲突
    tag_string = Column(String, nullable=True)  # 存储字符串形式的标签
    parsed = Column(Boolean, default=False)
    file_path = Column(String)
    file_type = Column(String)
    
    # 保留关系但重命名
    tags = relationship("Tag", secondary="document_tags", back_populates="documents")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())