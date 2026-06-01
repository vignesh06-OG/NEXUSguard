# 🛡️ NEXUSguard AI

NEXUSguard AI is an autonomous application security engine that integrates directly into your GitHub workflow. It automatically scans Pull Requests for security vulnerabilities, calculates risk scores, and provides actionable, line-by-line feedback to developers—all powered by Gemini 1.5 Flash.

## 🚀 Features
- **Autonomous Security Scanning:** Automatically analyzes PR diffs to identify exploitable vulnerabilities (SQLi, Command Injection, Secrets, etc.).
- **Smart Risk Scoring:** Assigns a 0-10 risk score to every PR, helping teams prioritize critical fixes.
- **Auto-Updating PR Comments:** Posts a professional security report directly to the PR. If you update the code, NEXUSguard edits its own comment to keep the conversation clean.
- **Interactive Dashboard:** Real-time visibility into your repo's security posture.

## 🛠️ Tech Stack
- **AI Core:** Gemini 1.5 Flash (via LangChain Google GenAI)
- **Agentic Workflow:** CrewAI for automated security reasoning
- **Frontend:** Streamlit for real-time dashboarding
- **Infrastructure:** GitHub API (PyGithub) for seamless PR integration

## 🏗️ How it works
1. **Trigger:** Click "Scan All Open PRs" or trigger via Webhooks.
2. **Analysis:** The AI agent analyzes the `diff`, identifies patterns, and evaluates risk.
3. **Report:** Findings are formatted into a clean Markdown table and posted/updated on GitHub.
   
⚡ Automated Security Analysis
NEXUSguard supports GitHub Webhooks for event-driven security scanning.

Setup: Deploy webhook_listener.py on a cloud service (e.g., Render/Railway).

Config: Set WEBHOOK_SECRET in your environment.

GitHub: Configure your repository webhook to point to the listener URL.


## 🚀 Setup Instructions
1. **Clone the repo:** `git clone https://github.com/vignesh06-OG/nexusguard-test`
2. **Install requirements:** `pip install -r requirements.txt`
3. **Configure Secrets:** Add these to your Streamlit Cloud secrets:
   ```toml
   GOOGLE_API_KEY = "your_gemini_api_key"
   GITHUB_TOKEN = "your_github_personal_access_token"
4. Deploy: Connect your repository to Streamlit Cloud and click deploy!

🛡️ Security
NEXUSguard uses strict safety filters to handle potentially sensitive code diffs while ensuring robust vulnerability detection.
   
   
   
