# AI套定额系统

基于AI智能匹配的工程造价定额套用系统。

## 功能特性

- 🤖 **AI智能匹配** - 根据工程描述自动匹配最合适的定额
- 📊 **费用自动计算** - 人工费、材料费、机械费、管理费、利润、税金
- 📚 **定额库管理** - 支持增删改查
- 📜 **历史记录** - 保存分析历史，支持导出
- 📥 **Excel导出** - 一键导出工程造价清单

## 技术栈

### 后端
- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - 异步ORM数据库操作
- **Pydantic** - 数据验证
- **SQLite** - 轻量级数据库

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vue Router** - 路由管理
- **Axios** - HTTP请求

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wjy520crl/AI-.git
cd AI-
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
python app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后自动初始化示例定额数据。

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端访问: http://localhost:3001
API代理: http://localhost:3001/api -> http://localhost:8000/api

## API文档

启动后端后访问: http://localhost:8000/docs

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/quotas | 获取定额列表 |
| GET | /api/quotas/{code} | 获取定额详情 |
| POST | /api/analyze | AI分析工程描述 |
| GET | /api/history | 获取分析历史 |
| DELETE | /api/history | 清空历史记录 |
| GET | /health | 健康检查 |

## 项目结构

```
ai-quota-system/
├── backend/
│   ├── app.py          # FastAPI应用入口
│   ├── models.py       # 数据库模型
│   ├── database.py     # 数据库配置
│   ├── config.py       # 配置参数
│   ├── schemas.py       # Pydantic模型
│   ├── services.py     # 业务逻辑
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 架构设计

### 分层架构

```
┌─────────────────────────────────┐
│         API路由层 (app.py)       │  处理HTTP请求/响应
├─────────────────────────────────┤
│         业务逻辑层 (services.py)  │  费用计算、AI匹配
├─────────────────────────────────┤
│         数据访问层 (models.py)    │  ORM模型定义
├─────────────────────────────────┤
│         数据库 (SQLite)           │  数据持久化
└─────────────────────────────────┘
```

### 费用计算公式

```
人工费 = Σ(人工消耗量 × 工日单价)
材料费 = Σ(材料消耗量 × 材料单价)
机械费 = Σ(机械台班消耗量 × 台班单价)
直接费 = 人工费 + 材料费 + 机械费
管理费 = 直接费 × 管理费率
利润 = (直接费 + 管理费) × 利润率
规费 = 直接费 × 规费率
税金 = (直接费 + 管理费 + 利润 + 规费) × 增值税率
合价 = 直接费 + 管理费 + 利润 + 规费 + 税金
```

## 配置说明

配置文件: `backend/config.py`

| 参数 | 默认值 | 说明 |
|------|--------|------|
| LABOR_PRICE | 150.0 | 工日单价(元/工日) |
| TAX_RATE | 0.09 | 增值税率 |
| REGULATION_RATE | 0.028 | 规费率 |

## 开发说明

### 添加新定额

```bash
curl -X POST http://localhost:8000/api/quotas \
  -H "Content-Type: application/json" \
  -d '{
    "code": "010101003",
    "name": "挖沟槽土方",
    "unit": "m³",
    "category": "土石方工程",
    "base_price": 30.0,
    "labor": {"工日": 0.48},
    "materials": {"水": 0.08},
    "machinery": {"挖掘机": 0.022}
  }'
```

### 提交代码

```bash
git add .
git commit -m "feat: 添加新功能"
git push
```

## License

MIT License
