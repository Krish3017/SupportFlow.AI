# SupportFlow AI - Complete Setup Guide

This guide will walk you through setting up the SupportFlow AI backend from scratch.

---

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] pip package manager
- [ ] Git (for cloning the repository)
- [ ] A Groq account (free tier available)
- [ ] A Resend account (free tier available)
- [ ] (Optional) A Google Cloud account for Gmail integration

---

## Step 1: Clone and Setup Environment

### 1.1 Clone Repository

```bash
git clone <your-repo-url>
cd backend
```

### 1.2 Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:** All packages should install successfully. This may take 2-3 minutes.

---

## Step 2: Get API Keys

### 2.1 Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `gsk_`)

### 2.2 Resend API Key

1. Go to [https://resend.com](https://resend.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `re_`)

---

## Step 3: Configure Environment

### 3.1 Create .env File

```bash
cp .env.example .env
```

### 3.2 Edit .env File

Open `.env` in your text editor and update:

```env
# Required - Add your actual keys
GROQ_API_KEY=gsk_your_actual_groq_key_here
RESEND_API_KEY=re_your_actual_resend_key_here

# Required - Update with your emails
SUPPORT_EMAIL=support@yourdomain.com
MANAGER_EMAIL=manager@yourdomain.com

# Optional - Use default for testing
FROM_EMAIL=onboarding@resend.dev
```

**Important:** 
- Never commit `.env` to git (it's in `.gitignore`)
- Replace placeholder values with real credentials
- For testing, you can use `onboarding@resend.dev` as `FROM_EMAIL`

---

## Step 4: Setup Knowledge Base

### 4.1 Verify Knowledge File Exists

```bash
ls data/company_knowledge.txt
```

### 4.2 Customize Knowledge Base (Optional)

Edit `data/company_knowledge.txt` with your company's:
- Policies
- Product information
- FAQ answers
- Procedures

### 4.3 Ingest Knowledge Base

```bash
python ingest.py
```

**Expected output:**
```
Ingested 15 chunks into ChromaDB at chroma_db
```

This creates the `chroma_db/` directory with vector embeddings.

---

## Step 5: Verify Setup

### 5.1 Check Configuration

Run a quick configuration check:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('✓ GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else '❌ MISSING')
print('✓ RESEND_API_KEY:', 'SET' if os.getenv('RESEND_API_KEY') else '❌ MISSING')
print('✓ Database path:', os.getenv('DATABASE_PATH', 'supportflow.db'))
print('✓ ChromaDB path:', os.getenv('CHROMA_DB_PATH', 'chroma_db'))
"
```

All items should show "SET".

### 5.2 Test Import

```bash
python -c "
from main import app
from database import create_tables
print('✓ All imports successful')
create_tables()
print('✓ Database tables created')
"
```

---

## Step 6: Run the Application

### 6.1 Start the Server

```bash
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     📧 Email Agent background task started.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6.2 Test Health Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "groq_api_configured": true,
  "resend_api_configured": true,
  "endpoints": {
    "chat": "/api/chat"
  }
}
```

### 6.3 Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order?"}'
```

You should see streaming response chunks.

---

## Step 7: (Optional) Setup Gmail Integration

**Note:** Only needed if you want email ticket processing.

### 7.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**:
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API"
   - Click **Enable**

### 7.2 Create OAuth Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Configure consent screen if prompted:
   - User type: **External**
   - Add your email as test user
4. Application type: **Desktop app**
5. Name: `SupportFlow AI`
6. Click **Create**

### 7.3 Download Credentials

1. Find your newly created OAuth client
2. Click the **download** icon (⬇)
3. Save as `credentials.json` in the `backend/` directory

### 7.4 Authorize Gmail Access

```bash
python gmail_reader.py
```

**What happens:**
1. Browser window opens
2. Google asks you to log in
3. Grant permissions to read/send emails
4. `token.json` is created automatically

**Expected output:**
```
✅ Token saved to 'token.json' — no login needed next time.
✅ Gmail authentication successful.
📬 Fetching 5 latest email(s) from INBOX...
```

### 7.5 Update .env for Gmail

```env
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
EMAIL_POLL_INTERVAL_MINUTES=2
```

### 7.6 Restart Server

The Email Agent will now automatically poll your Gmail inbox.

---

## Verification Checklist

After setup, verify everything works:

- [ ] Server starts without errors
- [ ] `/health` endpoint returns healthy status
- [ ] `/api/chat` endpoint accepts requests
- [ ] Responses stream correctly
- [ ] Database file is created (`supportflow.db`)
- [ ] ChromaDB directory exists (`chroma_db/`)
- [ ] (If Gmail enabled) Email agent polls inbox

---

## Troubleshooting

### "ModuleNotFoundError"

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY environment variable is required"

**Solution:** 
- Check `.env` file exists
- Verify `GROQ_API_KEY` is set in `.env`
- Restart the server

### "Ingestion failed: No such file"

**Solution:**
```bash
mkdir -p data
# Add your content to data/company_knowledge.txt
python ingest.py
```

### Gmail: "credentials.json not found"

**Solution:**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in backend directory

### Gmail: "Invalid credentials"

**Solution:**
```bash
# Delete old token and re-authorize
rm token.json
python gmail_reader.py
```

### Port 8000 already in use

**Solution:**
```bash
# Use a different port
PORT=8080 python main.py
```

### ChromaDB: "No such table"

**Solution:**
```bash
# Delete and recreate
rm -rf chroma_db
python ingest.py
```

---

## Next Steps

After successful setup:

1. **Customize the knowledge base** - Edit `data/company_knowledge.txt`
2. **Test with real queries** - Try different customer scenarios
3. **Configure email templates** - Customize in `services/email_service.py`
4. **Set up monitoring** - Check logs and database entries
5. **Deploy to production** - See deployment guide (if available)

---

## Development Tips

### Running in Development

```bash
# Auto-reload on code changes
python main.py
```

### Viewing Logs

All agents log their actions. Watch the console for:
- 🎯 Intent Agent
- 👤 Customer Intelligence Agent
- ⚡ Priority Agent
- 📚 Knowledge Agent
- 💬 Resolution Agent
- 🚨 Escalation Agent
- 📧 Email Agent

### Testing Without Frontend

Use `curl`, Postman, or write Python scripts to test the API.

### Updating Knowledge Base

After editing `data/company_knowledge.txt`:
```bash
rm -rf chroma_db
python ingest.py
```

---

## Security Reminders

**Never commit these files:**
- `.env` (contains API keys)
- `credentials.json` (Gmail OAuth)
- `token.json` (Gmail token)
- `*.db` (contains customer data)
- `chroma_db/` (vector store)

All are in `.gitignore` — verify before pushing:
```bash
git status
```

---

## Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review [troubleshooting section](#troubleshooting)
- Open an issue on GitHub
- Check agent logs for detailed error messages

---

## Success! 🎉

Your SupportFlow AI backend is now ready. The system will:
- ✅ Accept chat requests via API
- ✅ Classify customer intent automatically
- ✅ Retrieve relevant knowledge from the vector store
- ✅ Generate contextual responses
- ✅ Escalate complex issues intelligently
- ✅ (If enabled) Process email tickets automatically

Happy supporting! 🚀
