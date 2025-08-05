from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Black Rose API")

class ThemeSelection(BaseModel):
    theme: str

class PurchaseRequest(BaseModel):
    theme: str

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

@app.get("/")
def read_root():
    return {"message": "Black Rose Collective API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/themes/select")
def select_theme(sel: ThemeSelection):
    # Persist to storage stub
    return {"selected": sel.theme}

@app.post("/payment/charge")
def payment(req: PurchaseRequest):
    provider = os.getenv("PAYMENT_PROVIDER_URL", "")
    return {"status": "processed", "theme": req.theme, "provider": provider}

@app.post("/admin/override")
def admin_override(sel: ThemeSelection, token: str = Header(..., alias="X-Admin-Token")):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"granted": sel.theme}
