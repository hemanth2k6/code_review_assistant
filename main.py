from fastapi import FastAPI
from app.api.webhooks import router as webhook_router
app=FastAPI(title="ai code reviewer")
app.include_router(webhook_router,prefix="/api/v1")
@app.get("/")
def health_check():
    return {"status":"The ai code reviewer server is up and running"}