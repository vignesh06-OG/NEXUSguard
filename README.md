# 🛡️ NEXUSguard AI
**Intelligent Multi-Agent PR Reviewer & Token Optimizer**

[![Built with Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![Powered by CrewAI](https://img.shields.io/badge/Powered_by-CrewAI-black?style=for-the-badge)](https://www.crewai.com/)
[![LLM: Gemini](https://img.shields.io/badge/LLM-Google_Gemini-8E75B2?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)
[![Hackathon](https://img.shields.io/badge/Open_Source-Hackathon_2026-brightgreen?style=for-the-badge)](https://oshack.xyz/)

> **Live Demo:** [🔗 Click here to view the NEXUSguard Dashboard](https://nexusguard.streamlit.app/) *(Insert your actual Streamlit link here)*

## 🚀 The Vision
In the modern CI/CD pipeline, reviewing Pull Requests (PRs) for security vulnerabilities and logical errors takes immense developer hours. Furthermore, running large language models on huge codebases often results in massive token wastage and high API costs. 

**NEXUSguard AI** solves both problems simultaneously. It is an autonomous, multi-agent system that deeply analyzes GitHub PRs, catches security risks, and actively optimizes prompt token usage before querying the LLM—saving both **Time** and **Compute Cost**.

---

## ✨ Key Features
- **🤖 Multi-Agent Architecture:** Utilizes `CrewAI` to deploy specialized agents (Security Analyst, Code Optimizer, and Review Summarizer) working in tandem.
- **🔍 Automated PR Scanning:** Directly fetches open Pull Requests from GitHub and runs a comprehensive vulnerability scan.
- **📉 Token & Cost Optimization:** Integrated with our custom token-management logic to mathematically reduce input tokens without losing context, significantly reducing Gemini API costs.
- **📊 Interactive Dashboard:** A clean, real-time Streamlit UI providing instant feedback, Risk Scores, and detailed PR telemetry.
- **🛡️ Failsafe Executions:** Built-in error handling and graceful fallbacks for API throttling and authentication limits.

---

## 🛠️ Tech Stack
* **Frontend:** Python, Streamlit
* **AI & Orchestration:** CrewAI, Google Gemini (`langchain-google-genai`)
* **Version Control Integration:** PyGithub
* **Environment Management:** Python `python-dotenv`, Streamlit Secrets

---

## 💻 Local Setup & Installation

**1. Clone the repository**
```bash
2. Install Dependencies

Bash
pip install -r requirements.txt

3. Configure Environment Variables
Create a .env file in the root directory and add your API keys:

Code snippet
GOOGLE_API_KEY="your_gemini_api_key_here"
GITHUB_TOKEN="your_github_personal_access_token_here"

4. Run the Application
Bash
streamlit run app.py

⚡ Automated Security Analysis
NEXUSguard supports GitHub Webhooks for event-driven security scanning.
Setup: Deploy webhook_listener.py on a cloud service (e.g., Render/Railway).
Config: Set WEBHOOK_SECRET in your environment.
GitHub: Configure your repository webhook to point to the listener URL.

🔐 Security & Safety
NEXUSguard uses strict safety filters to handle potentially sensitive code diffs while ensuring robust vulnerability detection and preventing AI model misuse.

🔮 Future Roadmap (Post-Hackathon Goals)
[ ] Implement deeper Webhook integrations for automated PR triggers.

[ ] Add strict facial consistency mode for visual asset PRs (tracking UI/UX changes).

[ ] Expand the Multi-Access Edge Computing (MEC) simulation features for network-related code reviews.

Built with ❤️ by Vignesh for the Elite Coders Open Source Hackathon 2026.
git clone [https://github.com/vignesh06-OG/NEXUSguard.git](https://github.com/vignesh06-OG/NEXUSguard.git)
cd NEXUSguard
