from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from payload_engine.injector import Injector

app = FastAPI(title="Payload Service")

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

injector = Injector()

@app.post("/inject")
def inject_payloads(attack_object: dict):
    result = injector.inject(attack_object)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result