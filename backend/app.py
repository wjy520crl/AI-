"""AI套定额系统 - FastAPI后端"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, select
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./quota_system.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Quota(Base):
    __tablename__ = "quotas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    unit = Column(String(20))
    category = Column(String(50))
    description = Column(Text)
    labor = Column(JSON)
    materials = Column(JSON)
    machinery = Column(JSON)
    base_price = Column(Float)
    management_rate = Column(Float, default=0.105)
    profit_rate = Column(Float, default=0.07)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    result = Column(JSON)
    summary = Column(JSON)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

class QuotaItem(BaseModel):
    code: str; name: str; unit: str; category: str; quantity: float
    match_score: int; labor_cost: float; material_cost: float
    machinery_cost: float; management_fee: float; profit: float
    tax: float; subtotal: float; labor_detail: Dict; material_detail: Dict; machinery_detail: Dict

class AnalyzeRequest(BaseModel):
    description: str; quantity: float = 1.0

app = FastAPI(title="AI套定额系统", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class QuotaEngine:
    LABOR_PRICE = 150; TAX_RATE = 0.09; REGULATION_RATE = 0.028
    
    async def calculate_item(self, code, name, unit, category, match_score, quantity, labor=None, materials=None, machinery=None, management_rate=0.105, profit_rate=0.07):
        labor = labor or {}; materials = materials or {}; machinery = machinery or {}
        labor_cost = sum(amount * self.LABOR_PRICE for l_name, amount in labor.items())
        material_cost = sum(amount * 10 * quantity for m_name, amount in materials.items())
        machinery_cost = sum(amount * 100 * quantity for mc_name, amount in machinery.items())
        direct_cost = labor_cost + material_cost + machinery_cost
        management_fee = direct_cost * management_rate
        profit = (direct_cost + management_fee) * profit_rate
        regulation_fee = direct_cost * self.REGULATION_RATE
        tax = (direct_cost + management_fee + profit + regulation_fee) * self.TAX_RATE
        subtotal = direct_cost + management_fee + profit + regulation_fee + tax
        return QuotaItem(code=code, name=name, unit=unit, category=category, quantity=quantity, match_score=match_score,
            labor_cost=round(labor_cost * quantity, 2), material_cost=round(material_cost, 2), machinery_cost=round(machinery_cost, 2),
            management_fee=round(management_fee, 2), profit=round(profit, 2), tax=round(tax, 2), subtotal=round(subtotal, 2),
            labor_detail={k: round(v * quantity, 4) for k, v in labor.items()},
            material_detail={k: round(v * 10 * quantity, 2) for k, v in materials.items()},
            machinery_detail={k: round(v * 100 * quantity, 2) for k, v in machinery.items()})
    
    async def calculate_summary(self, items):
        total_labor = sum(i.labor_cost for i in items)
        total_material = sum(i.material_cost for i in items)
        total_machinery = sum(i.machinery_cost for i in items)
        direct_cost = total_labor + total_material + total_machinery
        return {"total_labor": round(total_labor, 2), "total_material": round(total_material, 2),
            "total_machinery": round(total_machinery, 2), "direct_cost": round(direct_cost, 2),
            "management_fee": round(sum(i.management_fee for i in items), 2), "profit": round(sum(i.profit for i in items), 2),
            "regulation_fee": round(direct_cost * self.REGULATION_RATE, 2), "tax": round(sum(i.tax for i in items), 2),
            "total_amount": round(sum(i.subtotal for i in items), 2)}

class AIService:
    KEYWORDS_MAP = {
        "土方": [("010101001", "挖一般土方"), ("010101002", "挖基坑土方")],
        "混凝土": [("010501001", "混凝土垫层"), ("010502001", "矩形柱")],
        "抹灰": [("011201001", "墙面抹灰")],
        "电气": [("030702001", "电气配线")],
    }
    def match(self, description: str) -> List:
        results = []
        for keyword, codes in self.KEYWORDS_MAP.items():
            if keyword in description:
                for code, name in codes:
                    results.append((code, name, 80))
        return results or [("010101001", "挖一般土方", 50)]

ai_service = AIService()

async def get_db():
    async with async_session() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_sample_data()

async def init_sample_data():
    async with async_session() as session:
        result = await session.execute(select(Quota))
        if not result.scalars().first():
            quotas = [
                Quota(code="010101001", name="挖一般土方", unit="m³", category="土石方工程", base_price=28.5, labor={"工日": 0.42}, materials={"水": 0.08}, machinery={"挖掘机": 0.024}),
                Quota(code="010101002", name="挖基坑土方", unit="m³", category="土石方工程", base_price=35.2, labor={"工日": 0.55}, materials={"水": 0.1}, machinery={"挖掘机": 0.028}),
                Quota(code="010501001", name="混凝土垫层", unit="m³", category="基础工程", base_price=420.0, labor={"工日": 0.88}, materials={"混凝土": 1.02}, machinery={"搅拌机": 0.04}),
                Quota(code="010502001", name="矩形柱", unit="m³", category="主体结构", base_price=580.0, labor={"工日": 1.12}, materials={"混凝土": 1.02}, machinery={"搅拌机": 0.05}),
                Quota(code="011201001", name="墙面抹灰", unit="m²", category="装饰工程", base_price=25.0, labor={"工日": 0.15}, materials={"砂浆": 0.02}, machinery={}),
                Quota(code="030702001", name="电气配线", unit="m", category="电气工程", base_price=15.0, labor={"工日": 0.05}, materials={"电线": 1.1}, machinery={}),
            ]
            session.add_all(quotas)
            await session.commit()

@app.get("/api/quotas")
async def get_quotas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quota).where(Quota.is_active == True))
    quotas = result.scalars().all()
    return {"items": [{"code": q.code, "name": q.name, "unit": q.unit, "category": q.category, "base_price": q.base_price, "management_rate": q.management_rate, "profit_rate": q.profit_rate} for q in quotas]}

@app.get("/api/quotas/{code}")
async def get_quota(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quota).where(Quota.code == code))
    quota = result.scalar_one_or_none()
    if not quota:
        raise HTTPException(status_code=404, detail="定额不存在")
    return {"code": quota.code, "name": quota.name, "unit": quota.unit, "category": quota.category, "base_price": quota.base_price, "labor": quota.labor, "materials": quota.materials, "machinery": quota.machinery}

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    matches = ai_service.match(request.description)
    engine2 = QuotaEngine()
    items = []
    for code, name, score in matches:
        result = await db.execute(select(Quota).where(Quota.code == code))
        quota = result.scalar_one_or_none()
        if quota:
            item = await engine2.calculate_item(code=code, name=quota.name, unit=quota.unit, category=quota.category,
                match_score=score, quantity=request.quantity, labor=quota.labor, materials=quota.materials,
                machinery=quota.machinery, management_rate=quota.management_rate, profit_rate=quota.profit_rate)
        else:
            item = await engine2.calculate_item(code=code, name=name, unit="项", category="未分类", match_score=score, quantity=request.quantity)
        items.append(item)
    summary = await engine2.calculate_summary(items)
    history = History(description=request.description, result=[item.dict() for item in items], summary=summary, total_amount=summary["total_amount"])
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return {"id": history.id, "description": request.description, "items": [item.dict() for item in items], "summary": summary}

@app.get("/api/history")
async def get_history(page: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(History).order_by(History.created_at.desc()).limit(page_size).offset((page-1)*page_size))
    histories = result.scalars().all()
    total = await db.scalar(select(History.id).count())
    return {"items": [{"id": h.id, "description": h.description[:50] + "..." if len(h.description) > 50 else h.description, "item_count": len(h.result.get("items", [])) if h.result else 0, "total_amount": h.total_amount, "created_at": h.created_at.isoformat() if h.created_at else None} for h in histories], "total": total or 0, "page": page, "page_size": page_size}

@app.get("/api/history/{history_id}")
async def get_history_detail(history_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(History).where(History.id == history_id))
    history = result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"id": history.id, "description": history.description, "result": history.result, "summary": history.summary, "created_at": history.created_at.isoformat() if history.created_at else None}

@app.delete("/api/history/{history_id}")
async def delete_history(history_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(History).where(History.id == history_id))
    history = result.scalar_one_or_none()
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(history)
    await db.commit()
    return {"success": True}

@app.delete("/api/history")
async def clear_history(db: AsyncSession = Depends(get_db)):
    await db.execute(History.__table__.delete())
    await db.commit()
    return {"success": True, "message": "已清空"}