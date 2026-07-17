"""公交出行平台 - 模拟后端 (端口 8001)"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, random
from datetime import datetime

app = FastAPI(title="公交后端")

class RouteQuery(BaseModel):
    origin: str; destination: str

class DispatchReq(BaseModel):
    route_id: str; date: str; passenger_count: int; vehicle_type: str = "大巴"

class PriceReq(BaseModel):
    distance_km: float; passenger_count: int; vehicle_type: str; date: str

@app.get("/api/health")
def health():
    return {"status": "UP", "service": "bus-backend", "time": datetime.now().isoformat()}

@app.post("/api/route/search")
def search(q: RouteQuery):
    data = {
        ("西湖","火车东站"): [{"route_id":"R001","route_name":"100路","duration_min":35,"stops":8,"price":2.0},
                            {"route_id":"R002","route_name":"28路","duration_min":45,"stops":12,"price":2.0}],
        ("西溪湿地","杭州西站"): [{"route_id":"R003","route_name":"149路","duration_min":30,"stops":6,"price":2.0}],
    }
    for (o,d), r in data.items():
        if q.origin in o or o in q.origin:
            if q.destination in d or d in q.destination:
                return r
    return []

@app.post("/api/dispatch/assign")
def assign(r: DispatchReq):
    if r.passenger_count > 100:
        return {"success": False, "message": "超过最大承载量"}
    return {"success": True, "vehicle_id": f"V{random.randint(100,999)}",
            "driver_name": random.choice(["王师傅(8年)","李师傅(12年)","张师傅(5年)"]),
            "plate_no": f"浙A{random.randint(10000,99999)}",
            "message": "车辆已分配"}

@app.post("/api/pricing/calculate")
def calc(r: PriceReq):
    base = r.distance_km * 8
    surcharge = {"大巴":500,"中巴":300,"商务车":200}.get(r.vehicle_type,0)
    extra = max(0, (r.passenger_count-30)*10)
    return {"standard_price": round(base+surcharge+extra,2),
            "breakdown": {"基础运费":f"{base:.2f}","车型附加":f"{surcharge:.2f}","人数附加":f"{extra:.2f}"},
            "discount_available": r.passenger_count>=50}

if __name__ == "__main__":
    print("🚌 后端启动: http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
