import jwt
import time
import httpx
from app.core.config import settings
import re
import base64

def generate_github_jwt()->str:
    payload={
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": settings.github_app_id
    }
    encoded_jwt = jwt.encode(payload, settings.github_private_key, algorithm="RS256")
    return encoded_jwt
async def get_installation_token(installation_id: int) -> str:
    jwt_token = generate_github_jwt()
    headers = {
        "Authorization" : f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["token"]
async def get_pr_diff(repo_full_name: str,pr_number: int, installation_id: int) -> str:
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

async def get_file_context(repo_full_name: str, file_path: str,installation_id: int) -> str:
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 404:
            return "File not found or was deleted"
        response.raise_for_status()
        data = response.json()
        file_content = base64.b64decode(data["content"]).decode("utf-8")
        return file_content
def extract_changed_files_from_diff(diff_text: str) -> list:
    file_paths = re.findall(r'^\+\+\+ b/(.+)$', diff_text, re.MULTILINE)
    return file_paths

async def post_pr_line_comment(
    repo_full_name: str,
    pr_number: int,
    installation_id: int,
    commit_id: str,
    file_path: str,
    line_number: int,
    body: str
) -> None:
    token = await get_installation_token(installation_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/comments"
    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": file_path,
        "line": line_number,
        "side": "RIGHT"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 422:
            print(f"Skipped comment on line {line_number}: That line wasn't part of the diff")
        else:
            response.raise_for_status()
            print(f"Successfully posted comment on line {line_number}")