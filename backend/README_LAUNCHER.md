# SupportFlow AI Launcher

**Single command to start all services in 3 separate terminal windows.**

## Usage

```bash
cd backend
python start_all.py
```

## What Happens

1. Detects venv (or uses system Python)
2. Opens 3 **completely separate** terminal windows:
   - **Terminal 1**: Telegram Bot logs
   - **Terminal 2**: API Server logs (http://localhost:8000)
   - **Terminal 3**: Email Monitor logs

## Stop Services

Press `Ctrl+C` in each terminal window.

## Requirements

Install dependencies first:
```bash
# Optional: create venv
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install
pip install -r requirements.txt
```

## Venv Detection

Searches for venv in:
- `Multi-Agent/venv`
- `Multi-Agent/.venv`
- `backend/venv`
- `backend/.venv`

Falls back to system Python if none found.

## Environment Variables

Required in `.env`:
```
GROQ_API_KEY=...
TELEGRAM_BOT_TOKEN=...
RESEND_API_KEY=...
SUPPORT_EMAIL=...
```

That's it. One file, one command.
