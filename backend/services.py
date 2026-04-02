"""
业务服务层 - 封装核心业务逻辑
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from config import config


@dataclass
class QuotaItemResult:
    """定额计算结果"""
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
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "code": self.code,
            "name": self.name,
            "unit": self.unit,
            "category": self.category,
            "quantity": self.quantity,
            "match_score": self.match_score,
            "labor_cost": self.labor_cost,
            "material_cost": self.material_cost,
            "machinery_cost": self.machinery_cost,
            "management_fee": self.management_fee,
            "profit": self.profit,
            "tax": self.tax,
            "subtotal": self.subtotal,
            "labor_detail": self.labor_detail,
            "material_detail": self.material_detail,
            "machinery_detail": self.machinery_detail,
        }


class QuotaCalculator:
    """
    定额费用计算引擎
    
    负责根据定额数据和工程量计算各项费用
    """
    
    def __init__(self):
        self.labor_price = config.LABOR_PRICE
        self.material_price = config.MATERIAL_PRICE
        self.machinery_price = config.MACHINERY_PRICE
        self.tax_rate = config.TAX_RATE
        self.regulation_rate = config.REGULATION_RATE
    
    def calculate(
        self,
        code: str,
        name: str,
        unit: str,
        category: str,
        match_score: int,
        quantity: float,
        labor: Optional[Dict] = None,
        materials: Optional[Dict] = None,
        machinery: Optional[Dict] = None,
        management_rate: float = 0.105,
        profit_rate: float = 0.07,
    ) -> QuotaItemResult:
        """
        计算单个定额项目的费用
        
        Args:
            code: 定额编号
            name: 定额名称
            unit: 计量单位
            category: 分类
            match_score: 匹配度
            quantity: 工程量
            labor: 人工消耗量字典
            materials: 材料消耗量字典
            machinery: 机械台班消耗量字典
            management_rate: 管理费率
            profit_rate: 利润率
        
        Returns:
            QuotaItemResult: 计算结果
        """
        # 确保默认值
        labor = labor or {}
        materials = materials or {}
        machinery = machinery or {}
        
        # 1. 计算人工费
        labor_cost = sum(
            amount * self.labor_price 
            for _, amount in labor.items()
        )
        
        # 2. 计算材料费
        material_cost = sum(
            amount * self.material_price * quantity
            for _, amount in materials.items()
        )
        material_detail = {
            name: round(amount * self.material_price * quantity, 2)
            for name, amount in materials.items()
        }
        
        # 3. 计算机械费
        machinery_cost = sum(
            amount * self.machinery_price * quantity
            for _, amount in machinery.items()
        )
        machinery_detail = {
            name: round(amount * self.machinery_price * quantity, 2)
            for name, amount in machinery.items()
        }
        
        # 4. 计算直接费
        direct_cost = labor_cost + material_cost + machinery_cost
        
        # 5. 计算管理费
        management_fee = direct_cost * management_rate
        
        # 6. 计算利润
        profit = (direct_cost + management_fee) * profit_rate
        
        # 7. 计算规费
        regulation_fee = direct_cost * self.regulation_rate
        
        # 8. 计算税金
        tax = (direct_cost + management_fee + profit + regulation_fee) * self.tax_rate
        
        # 9. 计算合价
        subtotal = direct_cost + management_fee + profit + regulation_fee + tax
        
        return QuotaItemResult(
            code=code,
            name=name,
            unit=unit,
            category=category,
            quantity=quantity,
            match_score=match_score,
            labor_cost=round(labor_cost * quantity, 2),
            material_cost=round(material_cost, 2),
            machinery_cost=round(machinery_cost, 2),
            management_fee=round(management_fee, 2),
            profit=round(profit, 2),
            tax=round(tax, 2),
            subtotal=round(subtotal, 2),
            labor_detail={k: round(v * quantity, 4) for k, v in labor.items()},
            material_detail=material_detail,
            machinery_detail=machinery_detail,
        )
    
    def calculate_summary(self, items: List[QuotaItemResult]) -> Dict:
        """
        计算费用汇总
        
        Args:
            items: 定额项目列表
        
        Returns:
            dict: 汇总数据
        """
        total_labor = sum(i.labor_cost for i in items)
        total_material = sum(i.material_cost for i in items)
        total_machinery = sum(i.machinery_cost for i in items)
        direct_cost = total_labor + total_material + total_machinery
        
        return {
            "total_labor": round(total_labor, 2),
            "total_material": round(total_material, 2),
            "total_machinery": round(total_machinery, 2),
            "direct_cost": round(direct_cost, 2),
            "management_fee": round(sum(i.management_fee for i in items), 2),
            "profit": round(sum(i.profit for i in items), 2),
            "regulation_fee": round(direct_cost * self.regulation_rate, 2),
            "tax": round(sum(i.tax for i in items), 2),
            "total_amount": round(sum(i.subtotal for i in items), 2),
        }


class AIMatcher:
    """
    AI智能匹配服务
    
    根据工程描述匹配相应定额
    """
    
    def __init__(self):
        self.keywords_map = config.AI_KEYWORDS
    
    def match(self, description: str) -> List[Tuple[str, str, int]]:
        """
        匹配定额
        
        Args:
            description: 工程描述
        
        Returns:
            List[(定额编号, 定额名称, 匹配度)]
        """
        results = []
        
        # 关键词匹配
        for keyword, quotas in self.keywords_map.items():
            if keyword in description:
                for code, name in quotas:
                    results.append((code, name, 80))
        
        # 未匹配时返回默认定额
        if not results:
            results = [("010101001", "挖一般土方", 50)]
        
        return results
