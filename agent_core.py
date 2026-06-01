import asyncio
import importlib
import logging
import os
from dotenv import load_dotenv
from github import Auth, Github
from google.ai.generativelanguage_v1beta.types import safety
from nexus_optimizer import NexusDiffOptimizer
from crewai import Agent, Crew, Process, Task

# agent_core.py Line 10 replacement
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

load_dotenv()
import streamlit as st
import os

# Streamlit Cloud ke secrets ko environment mein inject karne ka bridge
try:
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    if "GITHUB_TOKEN" in st.secrets:
        os.environ["GITHUB_TOKEN"] = st.secrets["GITHUB_TOKEN"]
except Exception:
    pass # Agar local pe chala rahe ho toh error nahi dega
import os
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_api_key(key_name: str) -> str | None:
    try:
        st = importlib.import_module("streamlit")
        secrets = getattr(st, "secrets", {})
        if secrets:
            value = secrets.get(key_name)
            if value:
                return value
    except ImportError:
        pass

    return os.getenv(key_name)


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_google_api_key() -> str:
    api_key = get_api_key("GOOGLE_API_KEY")
    if api_key:
        return api_key
    api_key = get_api_key("GEMINI_API_KEY")
    if api_key:
        return api_key
    raise ValueError("API Key missing. Check Streamlit secrets.")


# Initialize Nexus Token Optimizer
nexus_engine = NexusDiffOptimizer()


def fetch_open_prs(repo_name: str) -> list[dict]:
    github_token = get_required_env("GITHUB_TOKEN")
    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    repo = g.get_repo(repo_name)
    prs = repo.get_pulls(state="open", sort="updated")

    result = []
    for pr in prs:
        files_data = []
        total_chars = 0
        MAX_CHARS = 80000

        pr_total_original_tokens = 0
        pr_total_optimized_tokens = 0
        pr_total_tokens_saved = 0
        pr_total_cost_saved = 0.0

        for f in pr.get_files():
            if f.patch and total_chars < MAX_CHARS:
                nexus_result = nexus_engine.optimize_diff(f.patch)
                optimized_patch = nexus_result["optimized_diff"]

                pr_total_original_tokens += nexus_result.get("original_tokens", 0)
                pr_total_optimized_tokens += nexus_result.get("optimized_tokens", 0)
                pr_total_tokens_saved += nexus_result.get("tokens_saved", 0)
                pr_total_cost_saved += nexus_result.get("cost_saved_usd", 0.0)

                chunk = (
                    f"### File: `{f.filename}`\n"
                    f"**Status:** {f.status}\n\n"
                    f"```diff\n"
                    f"{optimized_patch[:3000]}\n"
                    f"```\n"
                )
                files_data.append(chunk)
                total_chars += len(chunk)

        result.append(
            {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "author": pr.user.login if pr.user else None,
                "diff": "\n".join(files_data),
                "pr_object": pr,
                "telemetry": {
                    "original_tokens": pr_total_original_tokens,
                    "optimized_tokens": pr_total_optimized_tokens,
                    "tokens_saved": pr_total_tokens_saved,
                    "cost_saved_usd": pr_total_cost_saved,
                },
            }
        )

    return result


def post_review_to_github(pr_object, comment_body: str):
    """Post or update a review comment on the PR.

    If a previous comment from the bot 'NEXUSguard' exists, update it instead of
    creating a new comment to avoid spam.
    """
    try:
        # Check existing issue comments for author 'NEXUSguard' or body marker
        for c in pr_object.get_issue_comments():
            try:
                author = getattr(c.user, "login", None)
                if author and author.lower() == "nexusguard":
                    c.edit(comment_body)
                    return
                # fallback: if the comment body contains the NEXUSguard marker, update it
                if "NEXUSguard" in (c.body or ""):
                    c.edit(comment_body)
                    return
            except Exception:
                # ignore individual comment errors
                continue

        # No existing comment found; create a new one
        pr_object.create_issue_comment(comment_body)
    except Exception:
        # Swallow exceptions to avoid failing the review loop; logging could be added
        return


def format_review_markdown(output_str: str, risk_score: int, pr_title: str | None = None, pr_url: str | None = None) -> str:
    """Return a concise Markdown-formatted review for posting to GitHub."""
    header = "## NEXUSguard Automated Review"
    badge = "🔴" if risk_score >= 7 else "🟡" if risk_score >= 4 else "🟢"
    title_line = f"**PR:** [{pr_title}]({pr_url})\n\n" if pr_title and pr_url else ""

    # Truncate very large outputs for comment body safety
    body = output_str or ""
    if len(body) > 12000:
        body = body[:12000] + "\n\n*(truncated)*"

    replaced_body = body.replace("\n", "<br/>")
    table = f"| Risk Score | Summary |\n|---:|---|\n| {risk_score}/10 | {replaced_body} |\n"

    footer = "---\n*🤖 Automated review by NEXUSguard — Powered by Gemini + CrewAI*"

    return "\n\n".join([header, title_line, f"**Result:** {badge}", table, footer])


def build_review_crew(pr_diff: str, pr_title: str):
    api_key = get_google_api_key()
    if api_key is None:
        raise ValueError("API Key missing. Check Streamlit secrets.")

    # Ensure an event loop exists for this thread (thread-safety)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    # Set safety settings to BLOCK_NONE for all harm categories to avoid blocking
    safety_settings = {
        cat: safety.SafetySetting.HarmBlockThreshold.BLOCK_NONE
        for cat in safety.HarmCategory
    }

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        safety_settings=safety_settings,
    )

    security_agent = Agent(
        role="Senior Application Security Engineer",
        goal="Find every exploitable security vulnerability in the code diff.",
        backstory=(
            "You are a battle-hardened AppSec engineer with 12 years of penetration testing experience. "
            "You think like an attacker. You know the OWASP Top 10 and CWE Top 25 by heart. "
            "You flag hardcoded secrets, injection flaws, auth issues, and insecure dependencies. "
            "You are methodical and paranoid by profession."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    quality_agent = Agent(
        role="Staff Software Engineer — Code Quality Specialist",
        goal="Identify logic bugs, performance issues, and code smell in the diff.",
        backstory=(
            "You are a pragmatic Staff Engineer who has reviewed thousands of PRs. "
            "You care about correctness, maintainability, and performance. "
            "You catch off-by-one errors, missing error handling, N+1 queries, memory leaks, "
            "and violations of DRY/SOLID principles. You do NOT re-flag security issues."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    synthesizer_agent = Agent(
        role="Engineering Manager — PR Review Synthesizer",
        goal="Synthesize all findings into a clear, structured, GitHub-ready review.",
        backstory=(
            "You are a senior engineering manager who writes PR reviews developers actually read and respect. "
            "You are direct but constructive. Your output is always clean GitHub Markdown."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    security_task = Task(
        description=(
            f"Analyze this PR titled \"{pr_title}\" for security vulnerabilities.\n\n"
            "DIFF TO ANALYZE:\n"
            f"{pr_diff}\n\n"
            "Check each category EXPLICITLY and report findings or CLEAN per category:\n"
            "1. Injection Flaws (SQL, Command, LDAP, NoSQL)\n"
            "2. Hardcoded Secrets / API Keys / Passwords\n"
            "3. Broken Authentication or Missing Authorization checks\n"
            "4. Sensitive Data Exposure (PII in logs, unencrypted storage)\n"
            "5. Insecure Dependencies (suspicious imports)\n"
            "6. Missing Input Validation / Sanitization\n"
            "7. Insecure Deserialization\n\n"
            "For each FINDING output:\n"
            "- SEVERITY: [CRITICAL | HIGH | MEDIUM | LOW]\n"
            "- FILE: filename\n"
            "- LINE: approximate line number\n"
            "- ISSUE: one sentence description\n"
            "- EXPLOIT: how an attacker could use this\n"
            "- FIX: corrected code snippet"
        ),
        expected_output=(
            "Structured security findings with severity, file, line, issue, exploit, and fix for each vulnerability found."
        ),
        agent=security_agent,
    )

    quality_task = Task(
        description=(
            f"Analyze this PR titled \"{pr_title}\" for code quality issues.\n"
            "Do NOT re-report security vulnerabilities.\n\n"
            "DIFF TO ANALYZE:\n"
            f"{pr_diff}\n\n"
            "Check for:\n"
            "1. Logic bugs and off-by-one errors\n"
            "2. Unhandled exceptions / missing try-catch\n"
            "3. Functions over 25 lines (complexity smell)\n"
            "4. Duplicate code (DRY violations)\n"
            "5. Missing type hints or incorrect types\n"
            "6. Performance anti-patterns (N+1 queries, blocking I/O, memory leaks)\n"
            "7. Dead code or unused imports\n\n"
            "For each FINDING output:\n"
            "- TYPE: [BUG | PERFORMANCE | STYLE | COMPLEXITY]\n"
            "- FILE: filename\n"
            "- LINE: approximate line number\n"
            "- ISSUE: one sentence description\n"
            "- FIX: corrected code snippet"
        ),
        expected_output=(
            "Structured quality findings with type, file, line, issue, and fix for each problem found."
        ),
        agent=quality_agent,
    )

    synthesis_task = Task(
        description=(
            "Using the security and quality reports, write the final GitHub PR review.\n\n"
            "Follow this EXACT markdown structure:\n\n"
            "## Executive Summary\n"
            "[2-3 sentence honest assessment]\n\n"
            "## Risk Score: X/10\n"
            "[One sentence justifying the score]\n\n"
            "## 🔴 Must Fix Before Merge\n"
            "[ONLY Critical and High items with FILE:LINE format]\n\n"
            "## 🟡 Should Fix Soon\n"
            "[Medium severity items]\n\n"
            "## 🟢 Suggestions (Optional)\n"
            "[Low severity items]\n\n"
            "## Summary Table\n"
            "| Severity | Count | Category |\n"
            "|----------|-------|----------|\n"
            "| 🔴 Critical | X | Security |\n"
            "| 🟠 High | X | Security/Quality |\n"
            "| 🟡 Medium | X | Quality |\n"
            "| 🟢 Low | X | Style |\n\n"
            "## Verdict\n"
            "[APPROVE / REQUEST CHANGES / NEEDS DISCUSSION] — [one sentence reason]\n\n"
            "Last line MUST be exactly:\n"
            "RISK_SCORE:N"
        ),
        expected_output=(
            "Complete GitHub-ready markdown review ending with RISK_SCORE:N on the last line."
        ),
        agent=synthesizer_agent,
    )

    crew = Crew(
        agents=[security_agent, quality_agent, synthesizer_agent],
        tasks=[security_task, quality_task, synthesis_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


def run_full_review(repo_name: str, post_to_github: bool = True):
    prs = fetch_open_prs(repo_name)

    if not prs:
        return []

    results = []
    for pr in prs:
        # Truncate very large diffs to avoid API request size errors
        pr_diff = pr.get("diff", "") or ""
        if len(pr_diff) > 15000:
            pr_diff = pr_diff[:15000]

        # Build crew with truncated diff
        try:
            crew = build_review_crew(pr_diff, pr["title"])
        except ValueError as e:
            logging.error("Failed to build review crew for PR %s: %s", pr.get("number"), e)
            results.append({
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title"),
                "pr_url": pr.get("url"),
                "author": pr.get("author"),
                "review": "",
                "summary": "API Authentication Failed",
                "risk_score": 0,
                "telemetry": pr.get("telemetry", {}),
                "error": str(e),
            })
            continue

        # Ensure an event loop exists for this thread before kickoff
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        # Run the crew and handle failures gracefully
        try:
            raw_output = crew.kickoff()
            output_str = str(raw_output)
        except Exception as e:
            logging.error("API authentication or model interaction failed for PR %s: %s", pr.get("number"), e)
            results.append({
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title"),
                "pr_url": pr.get("url"),
                "author": pr.get("author"),
                "review": "",
                "summary": "API Authentication Failed",
                "risk_score": 0,
                "telemetry": pr.get("telemetry", {}),
                "error": "API Authentication Failed",
            })
            continue

        # Default risk score to 0 when AI output doesn't include one
        risk_score = 0
        if "RISK_SCORE:" in output_str:
            try:
                score_part = output_str.split("RISK_SCORE:")[-1].strip()
                risk_score = int("".join(filter(str.isdigit, score_part[:3])))
                risk_score = max(0, min(10, risk_score))
            except (ValueError, IndexError):
                risk_score = 0

        if post_to_github:
            md = format_review_markdown(output_str, risk_score, pr.get("title"), pr.get("url"))
            post_review_to_github(pr["pr_object"], md)

        # Ensure consistent dictionary structure for successful runs
        results.append(
            {
                "pr_number": pr.get("number"),
                "pr_title": pr.get("title"),
                "pr_url": pr.get("url"),
                "author": pr.get("author"),
                "review": output_str,
                "summary": output_str,
                "risk_score": risk_score,
                "telemetry": pr.get("telemetry", {}),
            }
        )

    return results
