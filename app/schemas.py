from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, EmailStr


class HomepageData(BaseModel):
    total_users: int
    today_attendance: int
    attendance_rate: float
    dates: List[str]
    counts: List[int]

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class UserPagination(BaseModel):
    users: List[User]  # 假设User模型已经定义
    total: int
    
    class Config:
        from_attributes = True

# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 签到记录相关模型
class AttendanceRecordBase(BaseModel):
    user_id: int
    photo_path: str
    is_verified: bool = False

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecord(AttendanceRecordBase):
    id: int
    timestamp: datetime
    user: User  # 添加用户信息
    
    class Config:
        from_attributes = True


T = TypeVar('T')
class PagedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]  # 使用泛型类型
    
    class Config:
        from_attributes = True  # 更新为 Pydantic V2 的配置


class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    documents: List["Document"] = []

    class Config:
        from_attributes = True


# 文档
class Document(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    content: str
    tag_string: str  # 字符串形式的标签
    file_path: str
    file_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 循环引用处理
Tag.update_forward_refs()
Document.update_forward_refs()  