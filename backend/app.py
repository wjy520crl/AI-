"""
AI套定额系统 - FastAPI后端

架构说明:
- models.py: 数据库模型定义
- database.py: 数据库连接配置
- config.py: 项目配置参数
- services.py: 业务逻辑层
- schemas.py: API数据验证
- app.py: API路由层（入口）
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, Base, engine
from models import Quota, History
from schemas import (
    AnalyzeRequest, AnalyzeResponse, QuotaSchema, QuotaListResponse,
    HistoryListResponse, CreateQuotaRequest, SuccessResponse,
    HistorySummarySchema, QuotaItemSchema, SummarySchema
)
from services import QuotaCalculator, AIMatcher
from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 AI套定额系统启动中...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_sample_data()
    logger.info("✅ 系统初始化完成")
    yield
    logger.info("👋 系统已关闭")


app = FastAPI(title=config.API_TITLE, version=config.API_VERSION, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

calculator = QuotaCalculator()
matcher = AIMatcher()


async def init_sample_data():
    """初始化示例定额数据"""
    async with get_db() as db:
        result = await db.execute(select(Quota))
        if result.scalars().first():
            logger.info("定额数据已存在，跳过初始化")
            return
        sample_quotas = [
            Quota(code="010101001", name="挖一般土方", unit="m³", category="土石方工程", base_price=28.5,
                  labor={"工日": 0.42, "工长": 0.04}, materials={"水": 0.08}, machinery={"挖掘机": 0.024}),
            Quota(code="010101002", name="挖基坑土方", unit="m³", category="土石方工程", base_price=35.2,
                  labor={"工日": 0.55, "工长": 0.05}, materials={"水": 0.1}, machinery={"挖掘机": 0.028}),
            Quota(code="010103001", name="回填方", unit="m³", category="土石方工程", base_price=22.0,
                  labor={"工日": 0.35}, materials={"土": 1.15}, machinery={"夯实机": 0.08}),
            Quota(code="010501001", name="混凝土垫层", unit="m³", category="基础工程", base_price=420.0,
                  labor={"工日": 0.88, "混凝土工": 0.45}, materials={"混凝土": 1.02}, machinery={"搅拌机": 0.04}),
            Quota(code="010502001", name="矩形柱", unit="m³", category="主体结构", base_price=580.0,
                  labor={"工日": 1.12, "钢筋工": 0.6}, materials={"混凝土": 1.02, "钢筋": 0.08}, machinery={"搅拌机": 0.05}),
            Quota(code="011201001", name="墙面抹灰", unit="m²", category="装饰工程", base_price=25.0,
                  labor={"工日": 0.15}, materials={"砂浆": 0.02}, machinery={}),
            Quota(code="030702001", name="电气配线", unit="m", category="电气工程", base_price=15.0,
                  labor={"工日": 0.05}, materials={"电线": 1.1}, machinery={}),
        ]
        db.add_all(sample_quotas)
        await db.commit()
        logger.info(f"✅ 已初始化 {len(sample_quotas)} 条定额数据")


# ========== 定额管理 API ==========

@app.get("/api/quotas", response_model=QuotaListResponse, tags=["定额管理"])
async def get_quotas(db: AsyncSession = Depends(get_db)):
    """获取所有启用的定额列表"""
    try:
        result = await db.execute(select(Quota).where(Quota.is_active == True))
        quotas = result.scalars().all()
        return {"items": [QuotaSchema(**q.to_dict()) for q in quotas]}
    except Exception as e:
        logger.error(f"获取定额列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取定额列表失败")


@app.get("/api/quotas/{code}", response_model=QuotaSchema, tags=["定额管理"])
async def get_quota(code: str, db: AsyncSession = Depends(get_db)):
    """获取指定定额详情"""
    result = await db.execute(select(Quota).where(Quota.code == code))
    quota = result.scalar_one_or_none()
    if not quota:
        raise HTTPException(status_code=404, detail=f"定额 {code} 不存在")
    return QuotaSchema(**quota.to_dict())


@app.post("/api/quotas", response_model=SuccessResponse, tags=["定额管理"])
async def create_quota(request: CreateQuotaRequest, db: AsyncSession = Depends(get_db)):
    """创建新定额"""
    result = await db.execute(select(Quota).where(Quota.code == request.code))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"定额编号 {request.code} 已存在")
    quota = Quota(**request.model_dump())
    db.add(quota)
    await db.commit()
    logger.info(f"创建定额: {request.code} - {request.name}")
    return SuccessResponse(message=f"定额 {request.code} 创建成功")


@app.put("/api/quotas/{code}", response_model=SuccessResponse, tags=["定额管理"])
async def update_quota(code: str, request: CreateQuotaRequest, db: AsyncSession = Depends(get_db)):
    """更新定额"""
    result = await db.execute(select(Quota).where(Quota.code == code))
    quota = result.scalar_one_or_none()
    if not quota:
        raise HTTPException(status_code=404, detail=f"定额 {code} 不存在")
    for key, value in request.model_dump().items():
        setattr(quota, key, value)
    await db.commit()
    logger.info(f"更新定额: {code}")
    return SuccessResponse(message=f"定额 {code} 更新成功")


@app.delete("/api/quotas/{code}", response_model=SuccessResponse, tags=["定额管理"])
async def delete_quota(code: str, db: AsyncSession = Depends(get_db)):
    """删除定额（软删除）"""
    result = await db.execute(select(Quota).where(Quota.code == code))
    quota = result.scalar_one_or_none()
    if not quota:
        raise HTTPException(status_code=404, detail=f"定额 {code} 不存在")
    quota.is_active = False
    await db.commit()
    logger.info(f"删除定额: {code}")
    return SuccessResponse(message=f"定额 {code} 已删除")


# ========== AI分析 API ==========

@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["AI分析"])
async def analyze_description(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """分析工程描述，匹配定额并计算费用"""
    try:
        matches = matcher.match(request.description)
        logger.info(f"匹配结果: {request.description[:20]}... -> {[m[0] for m in matches]}")
        
        items = []
        for code, name, score in matches:
            result = await db.execute(select(Quota).where(Quota.code == code))
            quota = result.scalar_one_or_none()
            
            if quota:
                item = calculator.calculate(
                    code=code, name=quota.name, unit=quota.unit, category=quota.category,
                    match_score=score, quantity=request.quantity, labor=quota.labor,
                    materials=quota.materials, machinery=quota.machinery,
                    management_rate=quota.management_rate, profit_rate=quota.profit_rate,
                )
            else:
                item = calculator.calculate(
                    code=code, name=name, unit="项", category="未分类",
                    match_score=score, quantity=request.quantity,
                )
            items.append(item)
        
        summary = calculator.calculate_summary(items)
        
        history = History(
            description=request.description,
            result={"items": [i.to_dict() for i in items]},
            summary=summary,
            total_amount=summary["total_amount"],
        )
        db.add(history)
        await db.commit()
        await db.refresh(history)
        
        logger.info(f"分析完成: {history.id}, 总造价: ¥{summary['total_amount']}")
        
        return AnalyzeResponse(
            id=history.id,
            description=request.description,
            items=[QuotaItemSchema(**i.to_dict()) for i in items],
            summary=SummarySchema(**summary),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


# ========== 历史记录 API ==========

@app.get("/api/history", response_model=HistoryListResponse, tags=["历史记录"])
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取分析历史记录"""
    try:
        total = await db.scalar(select(func.count(History.id)))
        result = await db.execute(
            select(History).order_by(History.created_at.desc())
            .limit(page_size).offset((page - 1) * page_size)
        )
        histories = result.scalars().all()
        return HistoryListResponse(
            items=[HistorySummarySchema(**h.to_summary_dict()) for h in histories],
            total=total or 0, page=page, page_size=page_size,
        )
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")


@app.get("/api/history/{history_id}", tags=["历史记录"])
async def get_history_detail(history_id: int, db: AsyncSession = Depends(get_db)):
    """获取历史记录详情"""
    result = await db.execute(select(History).where(History.id == history_id))
    history = result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {
        "id": history.id, "description": history.description,
        "result": history.result, "summary": history.summary,
        "created_at": history.created_at.isoformat() if history.created_at else None,
    }


@app.delete("/api/history/{history_id}", response_model=SuccessResponse, tags=["历史记录"])
async def delete_history(history_id: int, db: AsyncSession = Depends(get_db)):
    """删除单条历史记录"""
    result = await db.execute(select(History).where(History.id == history_id))
    history = result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(history)
    await db.commit()
    logger.info(f"删除历史记录: {history_id}")
    return SuccessResponse(message="删除成功")


@app.delete("/api/history", response_model=SuccessResponse, tags=["历史记录"])
async def clear_history(db: AsyncSession = Depends(get_db)):
    """清空所有历史记录"""
    await db.execute(func.delete(History))
    await db.commit()
    logger.info("清空所有历史记录")
    return SuccessResponse(message="已清空全部历史记录")


# ========== 健康检查 ==========

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": config.API_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)