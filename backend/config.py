"""
项目配置 - 集中管理所有可配置参数
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """项目配置类"""
    
    # === 数据库 ===
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "quota_system.db")
    
    # === 费用计算参数 ===
    LABOR_PRICE: float = 150.0  # 工日单价（元/工日）
    MATERIAL_PRICE: float = 10.0  # 材料默认单价
    MACHINERY_PRICE: float = 100.0  # 机械默认台班单价
    TAX_RATE: float = 0.09  # 增值税率
    REGULATION_RATE: float = 0.028  # 规费率
    
    # === API参数 ===
    API_TITLE: str = "AI套定额系统"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # === 输入验证 ===
    MAX_DESCRIPTION_LENGTH: int = 2000
    MIN_DESCRIPTION_LENGTH: int = 5
    MIN_QUANTITY: float = 0.01
    MAX_QUANTITY: float = 999999.99
    
    # === 分页 ===
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # === AI服务 ===
    AI_KEYWORDS: dict = None
    
    def __post_init__(self):
        """初始化后的处理"""
        if self.AI_KEYWORDS is None:
            self.AI_KEYWORDS = {
                "土方": [("010101001", "挖一般土方"), ("010101002", "挖基坑土方")],
                "混凝土": [("010501001", "混凝土垫层"), ("010502001", "矩形柱")],
                "砌筑": [("010401001", "砖基础"), ("010401002", "砖墙")],
                "抹灰": [("011201001", "墙面抹灰")],
                "地面": [("011501001", "水泥砂浆地面"), ("011501002", "块料地面")],
                "电气": [("030702001", "电气配线")],
                "回填": [("010103001", "回填方")],
            }


# 全局配置实例
config = Config()
