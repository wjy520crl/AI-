"""
数据库模型 - 定义数据结构和表关系
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


class Quota(Base):
    """定额模型"""
    __tablename__ = "quotas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, index=True, nullable=False, comment="定额编号")
    name = Column(String(100), nullable=False, comment="定额名称")
    unit = Column(String(20), nullable=False, comment="计量单位")
    category = Column(String(50), nullable=False, comment="所属分类")
    description = Column(Text, comment="定额说明")
    labor = Column(JSON, comment="人工消耗量")
    materials = Column(JSON, comment="材料消耗量")
    machinery = Column(JSON, comment="机械台班消耗量")
    base_price = Column(Float, default=0, comment="基价")
    management_rate = Column(Float, default=0.105, comment="管理费率")
    profit_rate = Column(Float, default=0.07, comment="利润率")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, onupdate=func.now(), comment="更新时间")
    
    def to_dict(self) -> dict:
        """转换为字典，便于JSON序列化"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "unit": self.unit,
            "category": self.category,
            "description": self.description,
            "labor": self.labor or {},
            "materials": self.materials or {},
            "machinery": self.machinery or {},
            "base_price": self.base_price,
            "management_rate": self.management_rate,
            "profit_rate": self.profit_rate,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class History(Base):
    """分析历史记录模型"""
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=False, comment="工程描述")
    result = Column(JSON, comment="分析结果详情")
    summary = Column(JSON, comment="费用汇总")
    total_amount = Column(Float, default=0, comment="总造价")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    def to_summary_dict(self) -> dict:
        """转换为列表摘要"""
        return {
            "id": self.id,
            "description": self.description[:50] + "..." if len(self.description) > 50 else self.description,
            "item_count": len(self.result.get("items", [])) if self.result else 0,
            "total_amount": self.total_amount or 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
