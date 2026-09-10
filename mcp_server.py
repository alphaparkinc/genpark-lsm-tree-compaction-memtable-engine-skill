import sys
import json
from client import LSMTreeEngine

def main():
    engine = LSMTreeEngine()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        if method == "put":
            engine.put(params.get("key"), params.get("value"))
            res = {"status": "ok"}
        elif method == "get":
            val = engine.get(params.get("key"))
            res = {"value": val}
        else:
            res = {"error": "unknown method"}
        sys.stdout.write(json.dumps({"id": req.get("id"), "result": res}) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
