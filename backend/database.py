"""
数据库配置 - 统一管理数据库连接
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "quota_system.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# 异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 生产环境设为False减少日志
    pool_pre_ping=True,  # 连接前检测
)

# 会话工厂
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base类供模型继承
from sqlalchemy.orm import declarative_base
Base = declarative_base()


async def get_db():
    """
    数据库会话依赖
    
    使用FastAPI的Depends机制，确保：
    1. 请求结束时自动关闭连接
    2. 异常时自动回滚事务
    """
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库 - 创建所有表
    仅在应用启动时调用一次
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
