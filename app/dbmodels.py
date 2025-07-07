from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

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


# dbmodels.py
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)          # 文档名称
    description = Column(String)                # 文档描述
    content = Column(Text)                      # 文档内容
    tags = Column(String)                       # 文档标签（逗号分隔）

    file_path = Column(String)                  # 文档存储路径
    file_type = Column(String)                  # 文件类型（pdf/docx等）

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
