# CodeSlayer - Unified RFP Automation System

## Architecture

This system integrates three independent agent systems into a unified workflow:

1. **Sales-agent-main** (LangGraph Orchestrated AI System) - Magenta box
   - RFP scraping from government/private portals
   - Filtering and summarization
   - Best RFP selection

2. **Technichal_Agent-main** (Spec-Match Task) - Left Cyan box
   - Product matching from SKU repository
   - Semantic search using embeddings
   - Top 3 matches with scores

3. **pricing_agent** (Pricing Task) - Right Cyan box
   - Material cost calculation
   - Test cost calculation
   - Total pricing breakdown

## Unified Workflow

The `unified_workflow.py` orchestrates all three systems using LangGraph:

```
Scrape RFPs → Filter → Summarize → Select Best → 
  ↓
Spec-Match (find products) → 
  ↓
Pricing (calculate costs) → 
  ↓
Generate Response → 
  ↓
Package Output
```

## Quick Start

### 1. Set up Gemini API Key

This system uses **Google Gemini 2.0 Flash** for AI processing.

Create a `.env` file:
```bash
cp env.template .env
```

Add your Gemini API key to `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free API key from: https://aistudio.google.com/app/apikey

### 2. Install Dependencies

All dependencies from all three agents are consolidated in one file:

**Windows:**
```cmd
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
pip install -r requirements.txt
# Or using uv (much faster):
uv pip install -r requirements.txt
```

**This includes:**
- Sales-agent-main
- Technichal_Agent-main  
- pricing_agent
- Google Gemini AI SDK

> 💡 **Note**: On Linux, you may need `python3-pip` installed. On macOS, use `uv` for faster installs.

### 3. Run Unified Workflow (CLI)

**Windows:**
```cmd
python unified_workflow.py
```

**Linux/macOS:**
```bash
python3 unified_workflow.py
```

This will:
- Scrape RFPs from configured sources
- Filter and select the best RFP
- Match products from the SKU repository
- Calculate pricing
- Generate a draft response
- Save results to `rfp_final_response.json`

### 4. Run API Server

#### Option A: Using uvicorn (Recommended)

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Linux/macOS:**
```bash
source venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Production mode (no reload):**
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**With custom workers (production):**
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option B: Using Python directly

**Windows:**
```cmd
python api_server.py
```

**Linux/macOS:**
```bash
python3 api_server.py
```

**Server will start at:** http://localhost:8000

**Auto-reload:** Enabled with `--reload` flag (restarts on code changes)

> 💡 **See [Platform-Specific Setup](#-quick-start-commands) below for detailed Windows/Linux/macOS instructions**

---

### 5. Test All Endpoints

**Windows (Git Bash/WSL):**
```bash
bash test_endpoints.sh
```

**Linux/macOS:**
```bash
chmod +x test_endpoints.sh
./test_endpoints.sh
```

**Windows (PowerShell - Manual):**
See [Testing section](#testing) below for PowerShell commands.

**What the test script does:**
- ✅ Tests all 14 endpoints
- ✅ Validates responses
- ✅ Shows formatted JSON output
- ✅ Tests complete workflow flow

**Manual testing:**
See `test_endpoints.md` for individual endpoint examples.

**Interactive testing:**
Visit http://localhost:8000/docs for Swagger UI with try-it-out functionality.

> 💡 **See [Platform-Specific Testing](#testing) below for Windows/Linux/macOS specific commands**

---

### 📚 API Endpoints

**Interactive Docs**: http://localhost:8000/docs

All 14 endpoints matching architecture diagram:
- Data Sources: `/api/sku-repository`, `/api/rfp/scrape`, `/api/pricing-database`
- Tasks: `/api/spec-match`, `/api/pricing`
- Workflow: `/api/process-rfp`, `/api/status/{id}`, `/api/result/{id}`
- Output: `/api/response/approve`, `/api/response/generate-pdf/{id}`

**Quick Test:**
```bash
curl -X POST http://localhost:8000/api/process-rfp \
  -H "Content-Type: application/json" -d '{}'
```

## Project Structure

```
CodeSlayer/
├── unified_workflow.py       # Main unified workflow (LangGraph)
├── api_server.py             # FastAPI endpoint wrapper
├── requirements.txt          # Dependencies
├── README.md                 # This file
│
├── Sales-agent-main/         # Existing: RFP scraping & selection
│   ├── agents/
│   │   ├── rfp_scraper.py
│   │   ├── sales_agent.py
│   │   └── response_agent.py
│   ├── graph.py
│   └── main.py
│
├── Technichal_Agent-main/    # Existing: Spec matching
│   ├── query.py
│   ├── pdf_to_chroma.py
│   └── havells_parsed/
│       └── havells_catalogue_with_embeddings.json
│
└── pricing_agent/            # Existing: Pricing calculation
    ├── pricing_agent.py
    ├── main.py
    ├── product_processor.py
    ├── test_processor.py
    └── Pricing_Data_FMCG.xlsx
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Output Format

The unified workflow produces:

```json
{
  "rfp_details": {
    "title": "RFP Title",
    "due_date": "2024-12-31",
    "source": "https://...",
    "summary": "..."
  },
  "spec_matches": {
    "count": 5,
    "products": [
      {
        "query": "product requirement",
        "match_score": 0.95,
        "product": {...},
        "recommendation": "Product description"
      }
    ]
  },
  "pricing": {
    "total_material_cost": 50000,
    "total_test_cost": 5000,
    "grand_total": 55000,
    "pricing_table": [...]
  },
  "draft_response": "Dear Procurement Team...",
  "processing_summary": {
    "total_rfps_scraped": 150,
    "candidates_found": 12,
    "products_matched": 5,
    "generated_at": "2024-11-09T..."
  }
}
```

## 🚀 Quick Start Commands

### Platform-Specific Setup

#### 🪟 Windows (PowerShell/CMD)

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# PowerShell:
venv\Scripts\Activate.ps1
# CMD:
venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt
# Or using uv (faster):
uv pip install -r requirements.txt

# 4. Set up environment variables
copy env.template .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# 5. Start the server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# 6. In another terminal, run tests
# PowerShell:
bash test_endpoints.sh
# Or if Git Bash is installed:
./test_endpoints.sh
```

#### 🐧 Linux

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
# Or using uv (faster):
uv pip install -r requirements.txt

# 4. Set up environment variables
cp env.template .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
nano .env  # or use your preferred editor

# 5. Start the server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# 6. In another terminal, run tests
chmod +x test_endpoints.sh
./test_endpoints.sh
```

#### 🍎 macOS

```bash
# 1. Create virtual environment
python3 -m venv venv
# Or using uv (recommended):
uv venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
# Or using uv (faster):
uv pip install -r requirements.txt

# 4. Set up environment variables
cp env.template .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
nano .env  # or use your preferred editor

# 5. Start the server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# 6. In another terminal, run tests
chmod +x test_endpoints.sh
./test_endpoints.sh
```

---

### Server Management

#### Start Server

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

**Linux/macOS:**
```bash
source venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### Stop Server

**All Platforms:**
Press `Ctrl+C` in the terminal running uvicorn

**Windows (if Ctrl+C doesn't work):**
```powershell
# Find process
netstat -ano | findstr :8000
# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### Check if Server is Running

**Windows:**
```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:8000/ | Select-Object -Expand Content
# Or using curl (if available)
curl http://localhost:8000/
```

**Linux/macOS:**
```bash
curl http://localhost:8000/
```

#### Check What's Using Port 8000

**Windows:**
```powershell
# PowerShell
netstat -ano | findstr :8000
# Or
Get-NetTCPConnection -LocalPort 8000
```

**Linux:**
```bash
sudo lsof -i :8000
# Or
sudo netstat -tulpn | grep :8000
# Or
sudo ss -tulpn | grep :8000
```

**macOS:**
```bash
lsof -i :8000
# Or
netstat -an | grep 8000
```

#### Kill Process on Port 8000

**Windows:**
```powershell
# PowerShell - Find and kill
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($process) { Stop-Process -Id $process -Force }

# Or manually:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux:**
```bash
# Find PID
sudo lsof -t -i:8000
# Kill process
sudo kill $(sudo lsof -t -i:8000)
# Or force kill
sudo kill -9 $(sudo lsof -t -i:8000)
```

**macOS:**
```bash
# Find and kill
kill $(lsof -t -i:8000)
# Or force kill
kill -9 $(lsof -t -i:8000)
```

---

### Testing

#### Run All Endpoint Tests

**Windows (Git Bash or WSL):**
```bash
bash test_endpoints.sh
# Or if Git Bash:
./test_endpoints.sh
```

**Windows (PowerShell - Manual):**
```powershell
# Test root endpoint
Invoke-WebRequest -Uri http://localhost:8000/ | Select-Object -Expand Content

# Test spec-match
$body = @{
    query = "1.5 sq mm cable"
    top_k = 3
} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/api/spec-match -Method POST -Body $body -ContentType "application/json" | Select-Object -Expand Content
```

**Linux/macOS:**
```bash
chmod +x test_endpoints.sh
./test_endpoints.sh
```

#### Test Individual Endpoint

**Windows (PowerShell):**
```powershell
$body = '{"query": "1.5 sq mm cable", "top_k": 3}'
Invoke-WebRequest -Uri http://localhost:8000/api/spec-match -Method POST -Body $body -ContentType "application/json"
```

**Windows (with curl - if installed):**
```cmd
curl -X POST http://localhost:8000/api/spec-match -H "Content-Type: application/json" -d "{\"query\": \"1.5 sq mm cable\", \"top_k\": 3}"
```

**Linux/macOS:**
```bash
curl -X POST http://localhost:8000/api/spec-match \
  -H "Content-Type: application/json" \
  -d '{"query": "1.5 sq mm cable", "top_k": 3}' | python3 -m json.tool
```

#### View API Documentation

**All Platforms:**
- Open browser: http://localhost:8000/docs
- Or: http://localhost:8000/redoc

---

### Platform-Specific Notes

#### Windows

- **PowerShell Execution Policy**: If you get an error activating venv, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Path Separators**: Use backslashes (`\`) for paths in CMD, forward slashes (`/`) work in PowerShell
- **Python Command**: Use `python` instead of `python3` on Windows
- **curl**: Not available by default, use `Invoke-WebRequest` or install curl from https://curl.se/windows/

#### Linux

- **Python Version**: May need to use `python3` explicitly
- **Permissions**: May need `sudo` for port binding below 1024
- **Package Manager**: Install Python dependencies via system package manager if needed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-venv python3-pip
  # Fedora/RHEL
  sudo dnf install python3 python3-pip
  ```

#### macOS

- **Python Version**: macOS comes with Python 2.7, install Python 3 via Homebrew:
  ```bash
  brew install python3
  ```
- **uv**: Recommended package manager for faster installs:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Notes

- The workflow uses LangGraph for orchestration (as per architecture)
- All three existing systems are integrated without major modifications
- Results are saved to `rfp_final_response.json`
- The API server provides async processing with job tracking
- Use `--reload` flag for development (auto-restart on code changes)
- Remove `--reload` for production deployment

