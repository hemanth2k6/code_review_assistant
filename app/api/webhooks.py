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
        pr_number = payload["pull_request"]["number"]
        repo_full_name = payload["repository"]["full_name"]
        installation_id = payload["installation"]["id"]
        print(f"Received a Pull Request event! Action: {action} on {repo_full_name} PR #{pr_number}")
        if action in ["opened", "synchronize"]:
            from app.services.github import get_pr_diff, extract_changed_files_from_diff, get_file_context
            diff_text = await get_pr_diff(repo_full_name, pr_number, installation_id)
            changed_files = extract_changed_files_from_diff(diff_text)
            print(f"Files changed in this PR: {changed_files}")
            if changed_files:
                first_file = changed_files[0]
                file_context = await get_file_context(repo_full_name, first_file, installation_id)
                print(f"Successfully fetched context for {first_file} Length: {len(file_context)} characters")
        return {"status": "success","message":f"Pull request event '{action}' processed"}
    if event_type == "ping":
        print("Github sent a ping to test the connection")
        return {"status": "success","message": "Pong"}
    return {"status": "ignored", "message": f"Event '{event_type}' ignored"}