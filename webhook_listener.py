import asyncio
import hmac
import hashlib
import logging
import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from agent_core import run_full_review

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_webhook_secret() -> str:
    secret = os.getenv("WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("WEBHOOK_SECRET is not set")
    return secret


def verify_signature(body: bytes, signature_header: str | None, secret: str) -> None:
    if not signature_header:
        raise HTTPException(status_code=400, detail="Missing X-Hub-Signature-256 header")

    expected_prefix = "sha256="
    if not signature_header.startswith(expected_prefix):
        raise HTTPException(status_code=400, detail="Unsupported signature format")

    signature = signature_header[len(expected_prefix) :]
    computed_hmac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_hmac, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@app.post("/webhook")
async def webhook_listener(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    raw_body = await request.body()
    secret = get_webhook_secret()
    verify_signature(raw_body, x_hub_signature_256, secret)

    try:
        payload = await request.json()
    except Exception as exc:
        logging.error("Failed to parse webhook JSON: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_name = x_github_event or request.headers.get("X-GitHub-Event")
    logging.info("GitHub webhook received: event=%s", event_name)

    if event_name != "pull_request":
        return JSONResponse({"status": "ignored", "detail": "Event not handled"})

    action = payload.get("action")
    pr_number = payload.get("number")
    repo = payload.get("repository", {}).get("full_name")
    logging.info("Pull request event: action=%s repo=%s pr_number=%s", action, repo, pr_number)

    if action != "opened":
        return JSONResponse({"status": "ignored", "detail": f"PR action '{action}' not handled"})

    if not repo:
        logging.error("Repository full_name missing from payload")
        raise HTTPException(status_code=400, detail="Repository name missing")

    try:
        results = await asyncio.to_thread(run_full_review, repo, True)
        logging.info(
            "run_full_review completed for repo=%s pr_number=%s results=%d",
            repo,
            pr_number,
            len(results),
        )
    except Exception as exc:
        logging.exception("Error while running full review")
        raise HTTPException(status_code=500, detail="Failed to execute code review")

    return JSONResponse(
        {
            "status": "success",
            "detail": "Review triggered",
            "repository": repo,
            "pr_number": pr_number,
            "results_count": len(results),
        }
    )
