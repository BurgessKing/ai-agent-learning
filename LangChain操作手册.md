# LangChain 环境说明与操作手册

> 项目路径：`~/Desktop/learn/langchain-demo`

---

## 环境

| 项 | 值 |
|----|-----|
| Python | 3.11.15 |
| 虚拟环境 | `venv/`（项目隔离） |
| 核心包 | langchain, langchain-openai, langchain-core |
| Web框架 | FastAPI + uvicorn |
| HTTP客户端 | httpx |
| API Key | `.env` 文件（OPENAI_API_KEY=sk-xxx） |

---

## 启动

三种服务，各自一个终端：

```
服务              端口    启动命令                           依赖
────────────────────────────────────────────────────────────
模拟后端           8001    python backend_server.py          无
Agent CLI          无      python agent_core.py              后端
Agent API          8002    python agent_api.py               后端
```

**每次新开终端先激活环境**：

```bash
cd ~/Desktop/learn/langchain-demo
source venv/Scripts/activate
```

---

## 操作

```bash
# ── 后端 ──
curl http://127.0.0.1:8001/api/health                     # 健康检查
curl -X POST http://127.0.0.1:8001/api/route/search \     # 路线查询
  -H "Content-Type: application/json" \
  -d '{"origin":"西湖","destination":"火车东站"}'
curl -X POST http://127.0.0.1:8001/api/dispatch/assign \  # 车辆调度
  -H "Content-Type: application/json" \
  -d '{"route_id":"R001","date":"2024-01-15","passenger_count":35,"vehicle_type":"大巴"}'
curl -X POST http://127.0.0.1:8001/api/pricing/calculate \ # 报价计算
  -H "Content-Type: application/json" \
  -d '{"distance_km":300,"passenger_count":35,"vehicle_type":"大巴","date":"2024-01-15"}'

# ── Agent ──
python agent_core.py              # 命令行交互（输入 quit 退出）
python agent_api.py               # HTTP API（访问 http://localhost:8002/docs 看 Swagger）
curl "http://127.0.0.1:8002/api/agent/stream?message=查西湖到火车东站公交"  # 流式调用
```

---

## 对接真实后端

改 `tools.py` 第 1 行：

```python
BACKEND_URL = "http://localhost:8080"   # 改成你的 Spring Boot 端口
```

---

## 常见问题

| 现象 | 解决 |
|------|------|
| `ModuleNotFoundError: langchain` | 没激活 venv，执行 `source venv/Scripts/activate` |
| `APIError: Invalid API key` | `.env` 里 KEY 没配或格式不对（等号两边无空格） |
| `ConnectError` | 后端没启动，先跑 `python backend_server.py` |
| 端口被占用 | `netstat -ano | grep 8001` 查进程，改端口或 kill |
