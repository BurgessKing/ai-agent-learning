# AI Agent 强化学习计划

> Java 架构师 → AI Agent 开发工程师，4周高强度转型路线

[![Status](https://img.shields.io/badge/status-迭代中-orange)](https://github.com/BurgessKing/ai-agent-learning)
[![LangChain](https://img.shields.io/badge/LangChain-1.3.13-blue)](https://python.langchain.com)

---

## 📂 文档导航

| 模块 | 内容 | 天数 |
|------|------|------|
| [01-LLM与Agent基础](./docs/01-LLM与Agent基础.md) | Transformer、Tokenization、Prompt Engineering、ReAct、Plan-and-Execute、Python速成 | Day 1-7 |
| [02-Agent框架与RAG](./docs/02-Agent框架与RAG.md) | LangChain (LCEL/LangGraph)、RAG、上下文工程、Dify对比、班车调度实战项目 | Day 8-14 |
| [03-Java并发与事务](./docs/03-Java并发与事务.md) | 多线程/高并发 经典题目+答案、事务传播/隔离级别、分布式事务 | Day 15-18 |
| [04-Agent深度概念](./docs/04-Agent深度概念.md) | Plan-and-Execute深入、上下文工程四层模型、模型调优决策树、Multi-Agent协作协议 | Day 19-21 |
| [05-面试题与系统设计](./docs/05-面试题与系统设计.md) | 13道高频面试题（含答案）、系统设计题、LLM应用实战经验 | Day 22-23 |
| [06-公交平台AI融合架构](./docs/06-公交平台AI融合架构.md) | ⭐ 终极项目：真实公交出行平台 + AI Agent 全栈融合（车辆调度 + 报价规则） | Day 24-28 |
| [07-学习路线与资源](./docs/07-学习路线与资源.md) | 4周作息表、论文列表、框架文档、杭州目标企业 | — |

## 🛠 配套实战项目

| 项目 | 路径 | 说明 |
|------|------|------|
| **LangChain Agent Demo** | [langchain-demo/](./langchain-demo/) | Windows 本机从零搭建，Agent 调通后端 API 全流程 |
| 操作手册 | [LangChain操作手册.md](./LangChain操作手册.md) | 环境说明 + 启动命令 + curl 测试 + 问题速查 |

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:BurgessKing/ai-agent-learning.git

# 2. 运行 LangChain Demo
cd langchain-demo
python -m venv venv
source venv/Scripts/activate   # Windows git-bash
pip install langchain langchain-openai fastapi uvicorn httpx python-dotenv

# 3. 配置 API Key
echo "DEEPSEEK_API_KEY=sk-xxx" > .env
echo "OPENAI_BASE_URL=https://api.deepseek.com/v1" >> .env

# 4. 终端1: 启动后端
python backend_server.py

# 5. 终端2: 启动 Agent
python agent_core.py
```

## 📊 学习进度

```
Week 1 ████████░░  基础理论 + Python
Week 2 ████████░░  LangChain + RAG
Week 3 ████████░░  Java 深化 + Agent 深度
Week 4 ████████░░  面试 + 终极项目
        └─ 当前进度
```

## 🎯 目标

- **岗位**: 杭州 AI Agent 开发/架构
- **薪资**: 30-40K
- **背景**: 35岁 Java 架构师，公共交通领域 10 年
- **策略**: Java 保底 + Python Agent 加分 + 公交行业壁垒
