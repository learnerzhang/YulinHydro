from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from sqlalchemy import select, insert, update

# 声明基类
Base = declarative_base()

# database.py
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # 允许多线程访问
    echo=True  # 可选，查看SQL日志
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def create_table(Base):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# database.py
async def insert_data(table, data):
    async with AsyncSessionLocal() as session:
        stmt = insert(table).values(data)
        await session.execute(stmt)
        await session.commit()  # 明确提交

async def update_data(table, condition, data):
    async with AsyncSessionLocal() as session:
        stmt = update(table).where(condition).values(data)
        await session.execute(stmt)
        await session.commit()  # 明确提交

async def select_data(table, condition=None):
    session = AsyncSessionLocal()
    if condition:
        stmt = select(table).where(condition)
    else:
        stmt = select(table)
    result = await session.execute(stmt)
    return result.scalars().all()
