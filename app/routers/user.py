import logging
import os
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status, Cookie
from sqlalchemy import func, select
from app import base_crud, dbmodels, schemas, utils
from app.dbmodels import User
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.database import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Response, Cookie
from sqlalchemy.orm import Session
import tempfile
import hashlib
import string
import secrets
import jwt
import io

from app.routers.auth import get_current_active_user

# 示例缓存（生产环境请替换为Redis等持久化缓存）
cache = {}

# 新增Pydantic模型
class UserBase(BaseModel):
    username: str

class UserReister(UserBase):
    captcha: str
    password: str
    checkPass: str

class UserLogin(UserBase):
    password: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None

    # avatar: '',
    # name: '张三',
    # email: 'zhangsan@example.com',
    # phone: '13800138000',
    # password: ''


SECRET_KEY = "your-secret-key"  # 建议从环境变量读取
ALGORITHM = "HS256"

router = APIRouter()


def generate_captcha_text(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def create_captcha_image(text):
    width, height = 160, 60
    image = Image.new('RGB', (width, height), (255, 255, 255))
    try:
        font = ImageFont.truetype('arial.ttf', 36)
    except IOError:
        font = ImageFont.load_default()  # 回退到默认字体
    draw = ImageDraw.Draw(image)
    
    # 随机字符位置和扭曲
    for i, char in enumerate(text):
        x = 10 + i * 30 + secrets.randbelow(10)
        y = 5 + secrets.randbelow(15)
        angle = secrets.randbelow(30) - 15
        rotated_char = Image.new('RGBA', (50, 50), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(rotated_char)
        char_draw.text((0, 0), char, font=font, fill=(0, 0, 0))
        rotated_char = rotated_char.rotate(angle, expand=1)
        image.paste(rotated_char, (x, y), rotated_char)
    
    # 添加干扰线和噪点
    for _ in range(5):
        x1 = secrets.randbelow(width)
        y1 = secrets.randbelow(height)
        x2 = secrets.randbelow(width)
        y2 = secrets.randbelow(height)
        draw.line([(x1, y1), (x2, y2)], fill=(secrets.randbelow(200), secrets.randbelow(200), secrets.randbelow(200)), width=1)
    for _ in range(100):
        x = secrets.randbelow(width)
        y = secrets.randbelow(height)
        draw.point((x, y), fill=(secrets.randbelow(255), secrets.randbelow(255), secrets.randbelow(255)))
    
    image = image.filter(ImageFilter.SMOOTH)
    return image

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dbmodels.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    print("upload_avatar:", current_user)
    # 保存照片
    photo_filename = utils.save_uploaded_file(file)
    photo_path = utils.get_file_path(photo_filename)
    
    # 提取人脸编码
    face_encoding = utils.extract_face_encoding(photo_path)
    
    # 更新用户信息
    current_user.photo_path = photo_path
    current_user.face_encoding = face_encoding
    current_user.face_encoding_updated_at = datetime.now()
    current_user.avatar_path = photo_path  # 更新头像路径
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return {"message": "头像上传成功", "photo_filename": photo_filename, "photo_path": photo_path}

@router.get("/captcha")
async def get_captcha(response: Response):
    captcha_text = generate_captcha_text()
    captcha_key = secrets.token_urlsafe(16)  # 生成唯一键
    
    # 存储验证码（示例使用内存缓存，生产需用Redis等）
    cache[captcha_key] = captcha_text
    # 将键通过Cookie返回客户端
    response.set_cookie(key="captcha_key", value=captcha_key, max_age=300, httponly=True)
    
    # 生成图片
    image = create_captcha_image(captcha_text)
    byte_stream = io.BytesIO()
    image.save(byte_stream, format="PNG")
    byte_stream.seek(0)
    
    resp = Response(content=byte_stream.getvalue(), media_type="image/png")
    resp.set_cookie(
        key="captcha_key", 
        value=captcha_key, 
        httponly=True,
        max_age=300,  # 5 分钟
        path="/"
    )
    return resp


@router.post("/verify")
async def verify_captcha(user_input: str, captcha_key: Optional[str] = Cookie(None)):
    if not captcha_key:
        return {"status": "error", "message": "Missing captcha key"}
    stored_text = cache.get(captcha_key)
    if not stored_text:
        return {"status": "error", "message": "Invalid or expired captcha"}
    # 验证后删除缓存
    del cache[captcha_key]
    if user_input.upper() == stored_text:
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Invalid captcha"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserReister, 
                      captcha_key: str = Cookie(None),
                      db: AsyncSession = Depends(get_db)):
    from fastapi.responses import JSONResponse
    logger = logging.getLogger(__name__)
    logger.info(f"Received register request: {user.dict()}, captcha_key: {captcha_key}")

    if not captcha_key:
        return {"success":False, "message": "验证码已过期或未生成"}
    
    stored_text = cache.get(captcha_key)
    
    if not stored_text:
        return {"success":False, "message": "验证码已过期或无效"}
    
    if stored_text != user.captcha:
        return {"success":False, "message": "验证码输入错误"}
    
    # 验证后立即删除缓存，防止重复使用
    del cache[captcha_key]
    
    # 检查用户名是否已存在
    existing_user = await db.execute(select(User).where(User.username == user.username))
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        return {"success":False, "message": "用户名已被注册"}
    
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    is_admin = False
    if user.username == "admin" or user.username == "root":
        is_admin = True
    db_user = User(username=user.username, hashed_password=hashed_password, is_admin=is_admin, is_active=True)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"success":True, "data": db_user}


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(user: UserLogin, 
                      db: AsyncSession = Depends(get_db)):
    from fastapi.responses import JSONResponse
    logger = logging.getLogger(__name__)
    logger.info(f"Received login request: {user.dict()}")

    # 检查用户名是否已存在
    existing_user = await db.execute(select(User).where(User.username == user.username))
    existing_user = existing_user.scalar_one_or_none()
    if not existing_user:
        return {"success":False, "message": "用户名不存在"}
    
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if existing_user.hashed_password == hashed_password:
        # 生成JWT token
        token_data = {
            "sub": existing_user.username,
            "uid": existing_user.id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        print("user:", existing_user)
        return {"success":True, "data": {
            "uid": existing_user.id,
            "username": existing_user.username,
            "avatar": existing_user.avatar_path,
            "isAdmin": existing_user.is_admin,
            "token": token
        }}
    else:
        return {"success":False, "message": "密码输入错误"}

@router.get("/users", response_model=schemas.UserPagination)
async def search_users(
    keyword: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    # 构建查询
    base_query = select(dbmodels.User)
    count_query = select(func.count(dbmodels.User.id))
    
    if keyword:
        # 使用 ilike 进行模糊查询，不区分大小写
        base_query = base_query.where(dbmodels.User.username.ilike(f"%{keyword}%"))
        count_query = count_query.where(dbmodels.User.username.ilike(f"%{keyword}%"))
    
    # 执行总数量查询
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # 执行分页查询 - 修改部分
    users_query = base_query.offset(skip).limit(limit)
    users_result = await db.execute(users_query)
    
    # 使用 scalars().all() 可能会忽略分页，改用迭代方式
    users = [user for user in users_result.scalars()]
    
    return {"users": users, "total": total}

@router.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {
        'id': db_user.id,
        'username': db_user.username,
        'email': db_user.email,
        'phone_number': db_user.phone_number,
        'name': db_user.full_name,
        'avatar': db_user.avatar_path,
        'is_admin': db_user.is_admin,
        'is_active': db_user.is_active,
        'created_at': db_user.created_at,
        'full_name': db_user.full_name,
    }


@router.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone_number,
        "name": user.full_name,
        "avatar": user.avatar_path,
        "isAdmin": user.is_admin,
        "isActive": user.is_active,
        "created_at": user.created_at,
    }
    return {"success": True, "data": data, "code": 200}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.username:
        db_user.username = user.username

    if user.email:
        db_user.email = user.email

    if user.phone:
        db_user.phone_number = user.phone

    if user.name:
        db_user.full_name = user.name
    
    if user.avatar:
        db_user.avatar_path = user.avatar

    if user.password and (len(user.password) >= 6 and len(user.password) <= 16):
        db_user.hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    await db.commit()
    return {"data": db_user, "success": True, "code": 200}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    await db.delete(user)
    await db.commit()
    return {"message": "用户删除成功"}


# 上传人脸照片
@router.post("/upload-face")
async def upload_face_photo(
    file: UploadFile = File(...),
    current_user: dbmodels.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # 保存照片
    photo_filename = utils.save_uploaded_file(file)
    photo_path = utils.get_file_path(photo_filename)
    
    # 提取人脸编码
    face_encoding = utils.extract_face_encoding(photo_path)
    
    # 更新用户人脸编码
    updated_user = base_crud.update_user_face_encoding(db, current_user.id, face_encoding)
    
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新人脸信息失败")
    
    return {"message": "人脸信息更新成功", "photo_filename": photo_filename}


# 删除签到记录
@router.delete("/attendance-records/{record_id}", response_model=schemas.AttendanceRecord)
async def delete_attendance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: dbmodels.User = Depends(get_current_active_user)
):
    # 检查记录是否存在
    record = await base_crud.get_attendance_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 检查记录是否属于当前用户
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该记录")
    
    # 删除记录
    await base_crud.delete_attendance_record(db, record_id)
    return record


# 在文件顶部添加导入
from typing import TypeVar, Generic
@router.get("/attendance-records", response_model=schemas.PagedResponse[schemas.AttendanceRecord])
async def get_my_attendance_records(
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100),
    current_user: dbmodels.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    records = await base_crud.get_attendance_records_by_user(db, user_id=current_user.id, skip=skip, limit=page_size)
    
    # 将 ORM 对象转换为 Pydantic 模型
    items = [schemas.AttendanceRecord.from_orm(record) for record in records]
    
    total = await base_crud.get_attendance_records_count_by_user(db, user_id=current_user.id)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items  # 使用转换后的模型
    }


@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    input_dir = "static/users"
    with tempfile.NamedTemporaryFile(delete=False, dir=input_dir, suffix='.jpg') as temp_file:
        temp_file.write(contents)
    
    file_basename = os.path.basename(temp_file.name)
    avatar = os.path.join(input_dir, file_basename)
    await db.commit()
    return {"message": "头像上传成功", "data": avatar, "code": 200, "success": True}