"""前端API vs 后端API 对照"""
import re

# 1. 从前端 url.js 提取所有 API 路径
frontend_apis = set()
with open(r"D:\project\transit\front\operationmanagement\src\api\url.js", "r", encoding="utf-8") as f:
    for line in f:
        # 提取 `/api/xxx` 或只 `/xxx`
        match = re.search(r'["\'](/[^"\']+)["\']', line)
        if match:
            path = match.group(1)
            # 去掉 ${API_HOSTNAME} 前缀（实际请求时不带）
            path = path.replace("${API_HOSTNAME}", "").replace("${WS_HOSTNAME}", "").replace("`", "")
            if path and not path.startswith("//"):
                # 提取方法: 注释里的 "GET" / "POST"
                method = "POST"  # 默认
                if "GET" in line.upper() or "get" in line.lower():
                    if "GET请求" in line or "GET" in line.upper().split("//")[-1] if "//" in line else False:
                        method = "GET"
                # 简化: 用 key 名判断
                key = line.split(":")[0].strip()
                if key.startswith("get") or key.startswith("find") or key.startswith("query"):
                    method = "GET"
                
                frontend_apis.add(path)

# 2. 从后端提取所有API路径（已从 extract_apis.py 拿到结果）
backend_apis = set()
with open(r"D:\project\local\ai-agent-learning\scripts\backend_apis.txt", "w") as out:
    pass  # will fill below

# 重新提取后端的干净路径
import os
controllers_dir = r"D:\project\transit\tx-bus"
for root, dirs, files in os.walk(controllers_dir):
    for f in files:
        if f.endswith("Controller.java"):
            with open(os.path.join(root, f), "r", encoding="utf-8") as ctrl:
                content = ctrl.read()
            # Class-level
            c_map = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']', content)
            prefix = c_map.group(1) if c_map else ""
            # Method-level
            for m in re.finditer(
                r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']',
                content
            ):
                url = (prefix + m.group(2)).replace("//", "/")
                # 标准化
                url = url.replace("{id}", "id").replace("{taskNo}", "taskNo")
                url = url.replace("{code}", "code").replace("{userId}", "userId")
                url = url.replace("{orderCode}", "orderCode")
                url = url.replace("{parentDictCode}", "parentDictCode")
                url = url.replace("{rootDictCode}", "rootDictCode")
                url = url.replace("{scheduleId}", "scheduleId")
                url = url.replace("{ruleId}", "ruleId")
                url = url.replace("{version}", "version")
                url = url.replace("{appKey}", "appKey")
                url = url.replace("{coupunId}", "coupunId")
                url = url.replace("{app}", "app")
                url = url.replace("{token}", "token")
                url = url.replace("{feedbackId}", "feedbackId")
                url = url.replace("{channel}", "channel")
                url = url.replace("{personNum}", "personNum")
                backend_apis.add(url)

# 3. 对照
# 前端路径标准化
frontend_norm = set()
for api in frontend_apis:
    api = api.split("?")[0]  # 去掉查询参数
    api = api.rstrip("/")
    frontend_norm.add(api)

backend_norm = set()
for api in backend_apis:
    api = api.split("?")[0].rstrip("/")
    backend_norm.add(api)

# 前缀匹配: 后端接口可能有多层前缀，尝试匹配
missing = []
found = []
fuzzy_found = []

for fe in sorted(frontend_norm):
    # 精确匹配
    if fe in backend_norm:
        found.append(fe)
        continue
    
    # 模糊匹配: 后端有路径包含前端路径或其一部分
    matched = False
    fe_parts = fe.strip("/").split("/")
    for be in backend_norm:
        be_parts = be.strip("/").split("/")
        # 如果前端路径是后端路径的后缀
        if len(fe_parts) >= 3 and len(be_parts) >= 3:
            # 比较最后3段
            if fe_parts[-3:] == be_parts[-3:]:
                fuzzy_found.append((fe, be))
                matched = True
                break
            # 比较最后2段
            if len(fe_parts) >= 2 and fe_parts[-2:] == be_parts[-2:]:
                fuzzy_found.append((fe, be))
                matched = True
                break
    
    if not matched:
        missing.append(fe)

print(f"前端API总数: {len(frontend_norm)}")
print(f"后端API总数: {len(backend_norm)}")
print(f"精确匹配: {len(found)}")
print(f"模糊匹配: {len(fuzzy_found)}")
print(f"缺失: {len(missing)}")
print("\n=== 模糊匹配详情 ===")
for fe, be in fuzzy_found:
    print(f"  前端: {fe}")
    print(f"  后端: {be}")
    print()

print("\n=== 缺失接口(前端有,后端无) ===")
for api in missing:
    print(f"  {api}")
