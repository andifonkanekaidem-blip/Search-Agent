# Research Agent

A research intelligence agent that searches the web, checks weather, and performs calculations — all from a single query, with real-time streaming of agent activity.

🔗 **Live Demo:** https://ekaandi-freelance-agent.hf.space

![Demo](assets/demo.gif)

---

## What it does

- Searches the web in real time using Tavily and returns structured summaries
- Fetches current weather for any location via Open-Meteo
- Solves math problems and runs calculations using a sandboxed Python executor with NumPy and SymPy support
- Rejects irrelevant queries (chitchat, vague requests) immediately without wasting API calls
- Streams agent activity to the UI in real time — you see every step as it happens

---

## How it works

The agent runs a manual decision loop — no LangChain, no LangGraph. On each step the LLM decides which tool to use, executes it, feeds the result back into context, and repeats until it has enough information to answer.

```
User query → Validate → Pick tool → Execute → Observe → Repeat → Final answer
```

Tool routing, state management, and context assembly are all written from scratch.

---

## Tools

| Tool | Purpose |
|---|---|
| `search` | Searches the web via Tavily |
| `weather` | Fetches current weather via Open-Meteo |
| `calculator` | Executes Python in a sandboxed environment with NumPy and SymPy |

---

## Tech Stack

- **Backend:** FastAPI, Python
- **LLM:** Gemini 2.0 Flash (Google AI Studio)
- **Search:** Tavily
- **Weather:** Open-Meteo
- **Code Execution:** Sandboxed exec with NumPy and SymPy
- **Frontend:** Vanilla HTML/CSS/JS, Jinja2 SSR
- **Deployment:** Hugging Face Spaces (Docker)

---

## Run Locally

```bash
git clone https://github.com/andifonkanekaidem-blip/Search-Agent.git
cd Search-Agent
pip install -r requirements.txt
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the server:

```bash
python app.py
```

Visit `http://localhost:8000`

---

## Environment Variables

| Variable | Where to get it |
|---|---|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) |
| `TAVILY_API_KEY` | [Tavily](https://tavily.com) |
