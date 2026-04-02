"""
API数据模型 - 定义请求/响应的数据结构
使用Pydantic进行数据验证
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from config import config


class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    description: str = Field(
        ...,
        min_length=config.MIN_DESCRIPTION_LENGTH,
        max_length=config.MAX_DESCRIPTION_LENGTH,
        description="工程描述"
    )
    quantity: float = Field(
        default=1.0,
        ge=config.MIN_QUANTITY,
        le=config.MAX_QUANTITY,
        description="工程量"
    )
    
    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        """验证描述不为空或纯空白"""
        if not v or not v.strip():
            raise ValueError("工程描述不能为空")
        return v.strip()


class QuotaItemSchema(BaseModel):
    """定额项目数据模型"""
    code: str
    name: str
    unit: str
    category: str
    quantity: float
    match_score: int
    labor_cost: float
    material_cost: float
    machinery_cost: float
    management_fee: float
    profit: float
    tax: float
    subtotal: float
    labor_detail: Dict
    material_detail: Dict
    machinery_detail: Dict


class SummarySchema(BaseModel):
    """费用汇总数据模型"""
    total_labor: float
    total_material: float
    total_machinery: float
    direct_cost: float
    management_fee: float
    profit: float
    regulation_fee: float
    tax: float
    total_amount: float


class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    id: int
    description: str
    items: List[QuotaItemSchema]
    summary: SummarySchema


class QuotaSchema(BaseModel):
    """定额数据模型"""
    code: str
    name: str
    unit: str
    category: str
    description: Optional[str] = None
    labor: Optional[Dict] = None
    materials: Optional[Dict] = None
    machinery: Optional[Dict] = None
    base_price: Optional[float] = None
    management_rate: Optional[float] = None
    profit_rate: Optional[float] = None


class QuotaListResponse(BaseModel):
    """定额列表响应"""
    items: List[QuotaSchema]
    total: Optional[int] = None


class HistorySummarySchema(BaseModel):
    """历史记录摘要"""
    id: int
    description: str
    item_count: int
    total_amount: float
    created_at: Optional[str] = None


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    items: List[HistorySummarySchema]
    total: int
    page: int
    page_size: int


class CreateQuotaRequest(BaseModel):
    """创建定额请求"""
    code: str = Field(..., min_length=3, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    unit: str = Field(..., max_length=20)
    category: str = Field(..., max_length=50)
    description: Optional[str] = None
    labor: Optional[Dict] = {}
    materials: Optional[Dict] = {}
    machinery: Optional[Dict] = {}
    base_price: float = Field(default=0, ge=0)
    management_rate: float = Field(default=0.105, ge=0, le=1)
    profit_rate: float = Field(default=0.07, ge=0, le=1)


class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: str = "操作成功"


class ErrorResponse(BaseModel):
    """通用错误响应"""
    success: bool = False
    detail: str
