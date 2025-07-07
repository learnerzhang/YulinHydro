import asyncio
from contextlib import asynccontextmanager
from app.es_utils import create_index
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import AsyncSessionLocal, get_db, create_table, insert_data, select_data, engine
import uvicorn
from sqlalchemy import text
from app.routers import auth, kgapi, user, admin, documentapi

app = FastAPI(title="榆林知识服务系统", description="基于FastAPI的榆林知识服务系统", version="1.0.0")

# 跨域设置
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8888",
    # 添加你的前端域名
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时的初始化代码（如果有）
    yield

app = FastAPI(lifespan=lifespan)  # 将lifespan函数传递给FastAPI实例
app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由设置
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理员"])
app.include_router(kgapi.router, prefix="/api/kgapi", tags=["KG"])
app.include_router(documentapi.router, prefix="/api/documentapi", tags=["docs"])


@app.on_event("startup")
async def startup_event():
    create_index()  # 确保应用启动时索引已创建

@app.get("/")
def read_root():
    return {"Hello": "Welcome to YuLin KG System"}    


async def init_db():
    from app.dbmodels import Base
    await create_table(Base)
    # 启用WAL模式
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL;"))  # 正确写法
        
if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run(app, host="0.0.0.0", port=5000)
    