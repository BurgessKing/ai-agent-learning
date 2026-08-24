"""提取 transit-bus 和 transit-driver 所有接口路径"""
import re, os, json

base = r"D:/project/transit/tx-bus"
controllers = []

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith("Controller.java"):
            controllers.append(os.path.join(root, f))

endpoints = []

for path in controllers:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract class-level RequestMapping
    class_map = re.search(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
    class_prefix = class_map.group(1) if class_map else ""

    # Extract method-level mappings
    for m in re.finditer(
        r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']',
        content
    ):
        method = m.group(1).replace("Mapping", "").upper()
        if method == "REQUEST":
            method = "ANY"
        url = (class_prefix + m.group(2)).replace("//", "/")
        endpoints.append(f"{method} {url}")

# Sort and deduplicate
endpoints = sorted(set(endpoints))
for ep in endpoints:
    print(ep)
