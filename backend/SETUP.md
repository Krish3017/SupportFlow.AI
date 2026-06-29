# Backend Setup Guide

## Prerequisites

- Python 3.11+
- pip package manager
- Groq API key (get from https://console.groq.com/keys)

## Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Run setup tests
4. Start the server

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
# Windows: notepad .env
# Linux/Mac: nano .env
```

Your `.env` should look like:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

#### Step 4: Test Setup

```bash
python test_setup.py
```

You should see:
```
✓ All tests passed!
```

#### Step 5: Start Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

Server will start at: **http://localhost:8000**

## Verify Installation

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "groq_api_configured": true,
  "endpoints": {
    "chat": "/api/chat",
    "health": "/health"
  }
}
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Where is my order?\"}"
```

You should see streaming response chunks.

## Project Structure

```
backend/
├── main.py                   # FastAPI app entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .env                     # Your environment (create this)
├── README.md                # Documentation
├── SETUP.md                 # This file
├── test_setup.py            # Setup verification script
├── start.sh                 # Linux/Mac startup script
├── start.bat                # Windows startup script
│
├── routers/
│   ├── __init__.py
│   └── chat.py              # Chat endpoint with streaming
│
├── state/
│   ├── __init__.py
│   └── schema.py            # LangGraph state schema
│
└── agents/
    ├── __init__.py
    └── intent_agent.py      # Intent classification agent
```

## API Documentation

Once the server is running, visit:

- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Common Issues

### Issue: "GROQ_API_KEY environment variable is required"

**Solution:**
1. Make sure `.env` file exists
2. Verify `GROQ_API_KEY` is set in `.env`
3. Restart the server

### Issue: Import errors

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

### Issue: CORS errors from frontend

**Solution:**
- Frontend must run on `http://localhost:3000`
- Or update CORS origins in `main.py`

## Environment Variables

### Required

- `GROQ_API_KEY` - Your Groq API key

### Optional

You can add these to `.env`:

- `PORT=8000` - Server port
- `HOST=0.0.0.0` - Server host
- `LOG_LEVEL=info` - Logging level

## Development

### Run with Auto-Reload

```bash
python main.py
```

The server will automatically reload when you change files.

### View Logs

Intent classification logs appear in console:

```
--- Intent Classification ---
Intent: order_status
Sub-intent: delayed_order
Confidence: 0.98
Sentiment: negative
----------------------------
```

### Debug Mode

For more verbose logging, edit `main.py`:

```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="debug"  # Changed from "info"
)
```

## Testing with cURL

### Basic Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a refund"}'
```

### Order Status Query

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order #12345?"}'
```

### Technical Issue

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "The app keeps crashing"}'
```

## Testing with Python

Create `test_client.py`:

```python
import requests
import json

def test_chat(message):
    url = "http://localhost:8000/api/chat"
    data = {"message": message}

    print(f"User: {message}")
    print("Assistant: ", end="", flush=True)

    response = requests.post(url, json=data, stream=True)

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                event = json.loads(line[6:])
                if 'content' in event:
                    print(event['content'], end='', flush=True)
                elif event.get('done'):
                    print("\n")

# Test it
test_chat("Where is my order?")
test_chat("I want a refund")
test_chat("How do I reset my password?")
```

Run:
```bash
python test_client.py
```

## Next Steps

1. ✅ Backend is running
2. Connect frontend (update API URL in frontend)
3. Test end-to-end flow
4. Add more agents (Knowledge, Resolution)
5. Add database for conversation history
6. Add authentication

## Need Help?

- Check logs in console
- Verify `.env` configuration
- Test with cURL first before frontend
- Check that port 8000 is not blocked by firewall

## Production Deployment

For production, consider:

1. **Environment Variables:**
   - Use proper secret management
   - Don't commit `.env` to git

2. **Security:**
   - Enable HTTPS
   - Add authentication
   - Rate limiting

3. **Scaling:**
   - Use gunicorn with multiple workers
   - Add load balancer
   - Deploy to cloud (AWS, GCP, Azure)

4. **Monitoring:**
   - Add logging service
   - Error tracking (Sentry)
   - Performance monitoring

Example production command:
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Support

For issues or questions:
1. Check this guide
2. Review API docs at `/docs`
3. Check console logs
4. Verify environment setup
