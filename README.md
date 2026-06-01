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
git clone [https://github.com/vignesh06-OG/NEXUSguard.git](https://github.com/vignesh06-OG/NEXUSguard.git)
cd NEXUSguard
