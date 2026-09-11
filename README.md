# LearnPilot AI Content Pipeline

## Quick Start

### 1. Get your FREE Groq API key
→ https://console.groq.com  (sign up, go to API Keys, create key)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
# Mac / Linux
export GROQ_API_KEY=gsk_your_key_here

# Windows CMD
set GROQ_API_KEY=gsk_your_key_here

# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_key_here"
```

### 4. Run
```bash
python app.py
```
Open → http://localhost:5000

---

## Pipeline Flow

```
[Grade + Topic input]
       │
       ▼
┌─────────────────┐
│ Generator Agent │  →  { explanation, mcqs[3] }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reviewer Agent  │  →  { status: pass|fail, feedback[] }
└────────┬────────┘
         │  only if status = "fail"
         ▼
┌─────────────────┐
│ Refiner Agent   │  →  { explanation, mcqs[3] }  (1 pass max)
└─────────────────┘
```

## Files
```
eklavya_pipeline/
├── app.py              ← Flask server + AI agents
├── requirements.txt
├── README.md
└── static/
    └── index.html      ← Frontend UI
```

## Free Groq Models (change MODEL in app.py)
| Model               | Speed  | Quality |
|---------------------|--------|---------|
| llama3-8b-8192      | Fast   | Good    |
| llama3-70b-8192     | Medium | Better  |
| mixtral-8x7b-32768  | Medium | Great   |
