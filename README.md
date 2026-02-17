# ClarityAI Server

AI 驱动的需求对齐工具 - 后端服务

## 📖 项目简介

ClarityAI 是一个智能需求对齐工具，通过多轮交互式对话帮助用户从模糊的初步想法逐步明确为结构化项目需求。后端采用 Python Flask 框架，集成 Qwen AI API 提供智能问答和需求分析能力。

## ✨ 核心功能

- 🤖 **智能问题生成**：基于用户想法自动生成 5-10 个针对性问题
- 📝 **多轮需求对齐**：支持多轮交互，持续细化需求
- 📊 **报告自动生成**：基于问答内容生成结构化需求分析报告
- 📄 **文档导出**：支持导出 Markdown 格式项目文档
- 💾 **会话管理**：SQLite 数据库持久化存储项目数据
- 🔒 **Token 限额**：可配置每日 token 使用限额，控制成本
- 🔐 **API 密钥安全**：密钥存储在服务器端，不暴露给前端

## 🛠️ 技术栈

- **框架**：Flask 3.0.3
- **数据库**：SQLite
- **AI 集成**：OpenAI/Qwen API
- **PDF 生成**：ReportLab
- **CORS**：Flask-CORS

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/YCXHL/ClarityAI-Backend.git
cd ClarityAI-Backend
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv .
# Windows
Scripts\activate
# Linux/Mac
source bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

编辑 `.env` 文件：

```env
# Qwen API 配置
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-max

# 或者使用 OpenAI API
# OPENAI_API_KEY=your_openai_api_key_here

# 应用配置
SECRET_KEY=your_secret_key_here
PORT=5000

# Token 限额配置（每日总 token 数限制，设置为 0 表示无限制）
DAILY_TOKEN_LIMIT=0
```

### 5. 运行服务器

```bash
python run.py
```

服务器将在 `http://localhost:5000` 启动。

## 📡 API 接口

### 健康检查
```http
GET /api/health
```

### 生成问题
```http
POST /api/generate-questions
Content-Type: application/json

{
  "idea": "我想开发一个在线学习平台"
}
```

### 获取会话数据
```http
GET /api/session/<session_id>
```

### 提交答案
```http
POST /api/submit-answers
Content-Type: application/json

{
  "session_id": "uuid",
  "answers": [
    {"answer": "答案内容 1"},
    {"answer": "答案内容 2"}
  ]
}
```

### 继续细化需求
```http
POST /api/continue-with-feedback
Content-Type: application/json

{
  "session_id": "uuid",
  "feedback": "我想增加用户权限管理功能"
}
```

### 生成 PDF 文档
```http
POST /api/generate-pdf
Content-Type: application/json

{
  "session_id": "uuid"
}
```

### 下载文档
```http
GET /api/download-pdf/<session_id>
```

### 删除会话
```http
DELETE /api/session/<session_id>
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QWEN_API_KEY` | Qwen API 密钥 | - |
| `QWEN_BASE_URL` | Qwen API 基础 URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `QWEN_MODEL` | Qwen 模型名称 | `qwen-max` |
| `OPENAI_API_KEY` | OpenAI API 密钥（可选） | - |
| `SECRET_KEY` | Flask 密钥 | `dev-secret-key` |
| `PORT` | 服务端口 | `5000` |
| `DAILY_TOKEN_LIMIT` | 每日 token 限额（0 为无限制） | `0` |

### Token 限额

设置 `DAILY_TOKEN_LIMIT` 可控制每日 token 使用量：
- `0`：无限制
- `100000`：每日最多使用 100,000 个 token

达到限额后，AI 相关功能将暂停使用，但查看历史记录等功能不受影响。

## 📁 项目结构

```
ClarityAI-server/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py
│   └── utils/
│       ├── __init__.py
│       ├── qwen_api.py
│       ├── pdf_generator.py
│       ├── markdown_generator.py
│       └── token_limit.py
├── output/
├── clarity_ai.db
├── .env
├── requirements.txt
└── run.py  # 启动脚本
```


## 常见问题

### 1. 无法连接到 Qwen API
检查 `.env` 文件中的 `QWEN_API_KEY` 是否正确配置。

### 2. Token 限额生效
查看 `.env` 中的 `DAILY_TOKEN_LIMIT` 配置，设置为 `0` 可禁用限额。


## 📄 开源协议

GPL v3

## 👨‍💻 作者

Royan([Royan·小站](https://www.ycxhl.top))

