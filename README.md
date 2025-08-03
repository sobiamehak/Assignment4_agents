# 💼 AI-Based Bank Support Assistant (Multi-Agent System)

This project is an intelligent multi-agent system for handling customer support queries in a **banking environment**. It uses OpenAI’s model wrapped as Gemini, and it routes user queries based on their type (billing, technical, or general) to the appropriate virtual agent.

## 🚀 Features

- Smart routing of user queries using a **Triage Agent**
- Support for:
  - 💳 Billing issues (refunds, duplicate transactions, statements)
  - 🛠 Technical issues (OTP, login, app crashes)
  - 💬 General inquiries (branch timings, account types)
- Dynamic tool activation using **function decorators**
- Professional **Urdu-language responses** for billing queries
- Streaming response output with `run_streamed` agent logic

## 🧰 Tech Stack

- **Python 3.10+**
- `agents` framework (from Panaverse)
- `pydantic` for user input validation
- `dotenv` for environment variable management
- `openai` for model API interactions
- `asyncio` for asynchronous event streaming

## 📂 Project Structure

```plaintext
.
├── main.py                 # Main application logic
├── .env                   # Environment variables (contains GEMINI_API_KEY)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation (this file)
