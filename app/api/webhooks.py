from fastapi import APIRouter,Request,HTTPException
router=APIRouter()
@router.post("/webhook")
async def handle_webhook(request:Request):
    event_type=request.headers.get("X-GitHub-Event")
    try:
        payload=await request.json()
    except Exception:
        raise HTTPException(status_code=400,detail="Invalid json format")
    if event_type=="pull_request":
        action=payload.get("action")
        print(f"Received a Pull Request event action: {action}")
        return {"status":"success","message":f"Pull request event '{action}'"}
    if event_type=="ping":
        print("Github sent a ping to test the connection")
        return {"status":"success","message":"Pong"}
    return {"status":"ignored","message":f"Event '{event_type}' ignored"}