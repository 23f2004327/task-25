import json
from http.server import BaseHTTPRequestHandler
 
DATA = [
    {"region":"apac","latency_ms":135.13,"uptime_pct":97.75},
    {"region":"apac","latency_ms":221.52,"uptime_pct":98.48},
    {"region":"apac","latency_ms":140.78,"uptime_pct":97.67},
    {"region":"apac","latency_ms":116.59,"uptime_pct":97.89},
    {"region":"apac","latency_ms":110.61,"uptime_pct":98.239},
    {"region":"apac","latency_ms":163.62,"uptime_pct":98.323},
    {"region":"apac","latency_ms":197.63,"uptime_pct":97.208},
    {"region":"apac","latency_ms":199.58,"uptime_pct":98.859},
    {"region":"apac","latency_ms":145.86,"uptime_pct":99.02},
    {"region":"apac","latency_ms":241.1,"uptime_pct":99.157},
    {"region":"apac","latency_ms":190.25,"uptime_pct":97.585},
    {"region":"apac","latency_ms":119.06,"uptime_pct":97.766},
    {"region":"emea","latency_ms":132.89,"uptime_pct":97.148},
    {"region":"emea","latency_ms":166.81,"uptime_pct":98.716},
    {"region":"emea","latency_ms":208.86,"uptime_pct":97.155},
    {"region":"emea","latency_ms":175.23,"uptime_pct":98.052},
    {"region":"emea","latency_ms":215.35,"uptime_pct":99.476},
    {"region":"emea","latency_ms":133.48,"uptime_pct":99.21},
    {"region":"emea","latency_ms":169.11,"uptime_pct":99.097},
    {"region":"emea","latency_ms":210.44,"uptime_pct":99.093},
    {"region":"emea","latency_ms":102.2,"uptime_pct":97.241},
    {"region":"emea","latency_ms":226.76,"uptime_pct":98.076},
    {"region":"emea","latency_ms":196.49,"uptime_pct":99.419},
    {"region":"emea","latency_ms":201.78,"uptime_pct":98.452},
    {"region":"amer","latency_ms":115.77,"uptime_pct":98.498},
    {"region":"amer","latency_ms":203.34,"uptime_pct":97.374},
    {"region":"amer","latency_ms":222.23,"uptime_pct":98.82},
    {"region":"amer","latency_ms":133.21,"uptime_pct":98.285},
    {"region":"amer","latency_ms":179.99,"uptime_pct":99.125},
    {"region":"amer","latency_ms":212.05,"uptime_pct":98.106},
    {"region":"amer","latency_ms":187.32,"uptime_pct":97.209},
    {"region":"amer","latency_ms":137.41,"uptime_pct":98.976},
    {"region":"amer","latency_ms":154.59,"uptime_pct":98.727},
    {"region":"amer","latency_ms":179.81,"uptime_pct":97.545},
    {"region":"amer","latency_ms":154.24,"uptime_pct":98.82},
    {"region":"amer","latency_ms":154.98,"uptime_pct":99.113}
]
 
 
def percentile(values, p):
    v = sorted(values)
    k = (len(v) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)
 
 
def compute(regions, threshold):
    out = {}
    for region in regions:
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            continue
        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime_pct"] for r in rows]
        out[region] = {
            "avg_latency": sum(lat) / len(lat),
            "p95_latency": percentile(lat, 95),
            "avg_uptime": sum(up) / len(up),
            "breaches": sum(1 for x in lat if x > threshold),
        }
    return {"regions": out}
 
 
class handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
 
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
 
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()
 
    def do_GET(self):
        self._send(200, {"message": "POST JSON {regions, threshold_ms} to this URL"})
 
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            q = json.loads(self.rfile.read(n) or b"{}")
            res = compute(q.get("regions", []), float(q.get("threshold_ms", 0)))
            self._send(200, res)
        except Exception as e:
            self._send(400, {"error": str(e)})
 
