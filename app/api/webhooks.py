import hmac
import hashlib
from fastapi import APIRouter,Request,HTTPException,Header
from app.core.config import settings

router=APIRouter()
async def verify_signature(payload_body:bytes,signature_header:str):
    secret=settings.webhook_secret.encode()
    expected_signature=hmac.new(
        key=secret,
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    expected_signature_string=f"sha256={expected_signature}"
    if not hmac.compare_digest(expected_signature_string,signature_header):
        raise HTTPException(status_code=401,detail="Invalid signature. Nice try,hacker!")

@router.post("/webhook")
async def handle_webhook(request:Request,x_hub_signature_256:str=Header(None)):
    if not x_hub_signature_256:
        raise HTTPException(status_code=401,detail="Missing signature header")
    payload_body=await request.body()
    await verify_signature(payload_body,x_hub_signature_256)
    event_type=request.headers.get("X-GitHub-Event")
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400,detail="Invalid Json format")
    if event_type == "pull_request":
        action = payload.get("action")
        print(f"Received a Pull Request event! Action: {action}")
        return {"status": "success","message": f"Pull request event '{action}'"}
    if event_type == "ping":
        print("GitHub sent a ping to test the connection!")
        return {"status": "success", "message": "Pong"}
    return {"status": "ignored", "message": f"Event '{event_type}' ignored"}