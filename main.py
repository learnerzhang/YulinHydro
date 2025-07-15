import asyncio
from contextlib import asynccontextmanager
import os
from app.utils.es_utils import create_index
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import AsyncSessionLocal, get_db, create_table, insert_data, select_data, engine
import uvicorn
from sqlalchemy import text
from app.routers import auth, kgapi, tagapi, user, admin, documentapi

app = FastAPI(title="榆林知识服务系统", description="基于FastAPI的榆林知识服务系统", version="1.0.0")

# 跨域设置
origins = [
    "http://127.0.0.1:8081",
    "http://localhost:8081",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时的初始化代码（如果有）
    yield

app = FastAPI(lifespan=lifespan)  # 将lifespan函数传递给FastAPI实例
app.mount("/static", StaticFiles(directory="static"), name="static")
# 配置静态文件目录（确保路径正确）
documents_dir = os.path.join(os.path.dirname(__file__), "static", "documents")
app.mount("/static/documents", StaticFiles(directory=documents_dir), name="documents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8081", "http://localhost:8081"],  # 明确指定允许的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"]  # 新增：允许暴露所有响应头
)

# 路由设置
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
app.include_router(kgapi.router, prefix="/api/kgapi", tags=["KG"])
app.include_router(documentapi.router, prefix="/api/documentapi", tags=["docs"])
app.include_router(tagapi.router, prefix="/api/tagapi", tags=["tags"])

@app.on_event("startup")
async def startup_event():
    create_index()  # 确保应用启动时索引已创建

@app.get("/")
def read_root():
    return {"Hello": "Welcome to KG System"}    


async def init_db():
    from app.dbmodels import Base
    await create_table(Base)
    # 启用WAL模式
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL;"))  # 正确写法
        
if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run(app, host="0.0.0.0", port=5000)
    