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

```bash
pip install -r requirements.txt
```

This includes:
- Sales-agent-main
- Technichal_Agent-main  
- pricing_agent
- Google Gemini AI SDK

### 3. Run Unified Workflow (CLI)

```bash
python unified_workflow.py
```

This will:
- Scrape RFPs from configured sources
- Filter and select the best RFP
- Match products from the SKU repository
- Calculate pricing
- Generate a draft response
- Save results to `rfp_final_response.json`

### 4. Run API Server

```bash
python api_server.py
```

Then call the unified endpoint:

```bash
curl -X POST "http://localhost:8000/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{"rfp_urls": []}'
```

Get status:
```bash
curl "http://localhost:8000/api/status/{job_id}"
```

Get result:
```bash
curl "http://localhost:8000/api/result/{job_id}"
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

## Notes

- The workflow uses LangGraph for orchestration (as per architecture)
- All three existing systems are integrated without major modifications
- Results are saved to `rfp_final_response.json`
- The API server provides async processing with job tracking

