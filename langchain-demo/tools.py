"""Agent 工具 — 通过 HTTP 调用后端 API"""
import httpx, json
from langchain.tools import tool

BACKEND_URL = "http://127.0.0.1:8001"

@tool
def search_bus_route(origin: str, destination: str) -> str:
    """查询公交路线。参数: origin-出发地, destination-目的地"""
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f"{BACKEND_URL}/api/route/search", json={"origin": origin, "destination": destination})
            routes = r.json()
            if not routes:
                return f"未找到{origin}到{destination}的线路"
            result = f"{origin} → {destination} 共{len(routes)}条:\n"
            for i, rt in enumerate(routes, 1):
                result += f"  {i}. {rt['route_name']}  {rt['duration_min']}分钟 {rt['stops']}站 ¥{rt['price']}\n"
            return result.strip()
    except Exception as e:
        return f"查询失败: {e}"

@tool
def dispatch_vehicle(route_id: str, date: str, passenger_count: int, vehicle_type: str = "大巴") -> str:
    """车辆调度。参数: route_id, date(YYYY-MM-DD), passenger_count, vehicle_type"""
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f"{BACKEND_URL}/api/dispatch/assign", json={
                "route_id": route_id, "date": date,
                "passenger_count": passenger_count, "vehicle_type": vehicle_type
            })
            d = r.json()
            if d["success"]:
                return f"✅ 调度成功 | 车辆:{d['plate_no']} | 司机:{d['driver_name']} | {d['message']}"
            return f"❌ {d['message']}"
    except Exception as e:
        return f"调度失败: {e}"

@tool
def calculate_price(distance_km: float, passenger_count: int, vehicle_type: str, date: str) -> str:
    """报价计算。参数: distance_km, passenger_count, vehicle_type, date"""
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f"{BACKEND_URL}/api/pricing/calculate", json={
                "distance_km": distance_km, "passenger_count": passenger_count,
                "vehicle_type": vehicle_type, "date": date
            })
            d = r.json()
            return f"💰 ¥{d['standard_price']} | 明细:{json.dumps(d['breakdown'], ensure_ascii=False)}" + \
                   (" | 可申请团购折扣" if d.get("discount_available") else "")
    except Exception as e:
        return f"报价失败: {e}"

ALL_TOOLS = [search_bus_route, dispatch_vehicle, calculate_price]
