# 🧪 API Endpoint Test Commands

Complete test commands for all 14 endpoints with examples.

---

## 🏠 Root Endpoint

### Health Check
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "service": "CodeSlayer RFP Automation",
  "status": "online",
  "version": "1.0.0",
  "endpoints": { ... }
}
```

---

## 📦 Data Sources (Top Black Boxes)

### 1. SKU Repository
```bash
curl "http://localhost:8000/api/sku-repository?limit=10"
```

**Example:**
```bash
curl "http://localhost:8000/api/sku-repository?limit=5" | python3 -m json.tool
```

---

### 2. Scrape RFP Portals
```bash
curl -X POST "http://localhost:8000/api/rfp/scrape" \
  -H "Content-Type: application/json"
```

**With Custom URLs:**
```bash
curl -X POST "http://localhost:8000/api/rfp/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://etenders.gov.in/eprocure/app",
      "https://gem.gov.in/tenders"
    ]
  }'
```

**Response:**
```json
{
  "job_id": "scrape_1234567890",
  "status": "scraping",
  "message": "Scraping 2 RFP sources"
}
```

---

### 3. Historical Responses
```bash
curl "http://localhost:8000/api/historical-responses?limit=50"
```

---

### 4. Pricing Database
```bash
curl "http://localhost:8000/api/pricing-database"
```

**Expected Response:**
```json
{
  "products_count": 150,
  "tests_count": 25,
  "status": "available"
}
```

---

## 🔧 Spec-Match Task (Left Cyan Box)

### Find Top 3 Product Matches
```bash
curl -X POST "http://localhost:8000/api/spec-match" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "1.5 sq mm cable with high current rating",
    "top_k": 3
  }'
```

**More Examples:**

**Example 1: Heavy Duty Cables**
```bash
curl -X POST "http://localhost:8000/api/spec-match" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "heavy duty cables for industrial use",
    "top_k": 5
  }' | python3 -m json.tool
```

**Example 2: Specific Specifications**
```bash
curl -X POST "http://localhost:8000/api/spec-match" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "10 sq mm cable with thick insulation",
    "top_k": 5
  }' | python3 -m json.tool
```

**Expected Response:**
```json
{
  "query": "1.5 sq mm cable with high current rating",
  "matches_count": 3,
  "top_3_matches": [
    {
      "match_score": 0.95,
      "product": {
        "conductor_area_mm2": 1.5,
        "current_rating_amps": 20,
        "diameter_mm": 3.2,
        "weight_kg_per_km": 12.5
      }
    }
  ],
  "all_matches": [...]
}
```

---

## 💰 Pricing Task (Right Cyan Box)

### Calculate Pricing Table and Test Costs
```bash
curl -X POST "http://localhost:8000/api/pricing" \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_id": "RFP-2024-001",
    "technical_table": [
      {
        "item_no": 1,
        "description": "1.5 sq mm electrical cable",
        "quantity": 1000,
        "specifications": {
          "conductor_area_mm2": 1.5,
          "current_rating_amps": 20
        }
      },
      {
        "item_no": 2,
        "description": "2.5 sq mm electrical cable",
        "quantity": 500,
        "specifications": {
          "conductor_area_mm2": 2.5,
          "current_rating_amps": 30
        }
      }
    ],
    "rfp_summary": {
      "tests": ["Quality Test", "Performance Test", "Safety Test"]
    }
  }'
```

**Minimal Example:**
```bash
curl -X POST "http://localhost:8000/api/pricing" \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_id": "TEST-RFP",
    "technical_table": [
      {
        "item_no": 1,
        "description": "Product A",
        "quantity": 100
      }
    ],
    "rfp_summary": {
      "tests": ["Basic Test"]
    }
  }' | python3 -m json.tool
```

**Expected Response:**
```json
{
  "rfp_id": "RFP-2024-001",
  "total_material_cost": 50000,
  "total_test_cost": 5000,
  "grand_total": 55000,
  "pricing_table": [
    {
      "item_no": 1,
      "description": "1.5 sq mm electrical cable",
      "quantity": 1000,
      "unit_price": 50,
      "total_price": 50000
    }
  ],
  "test_breakdown": [
    {
      "test_name": "Quality Test",
      "cost": 2000
    }
  ]
}
```

---

## 🎯 Main Unified Workflow

### Process Complete RFP Pipeline
```bash
curl -X POST "http://localhost:8000/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**With Custom RFP URLs:**
```bash
curl -X POST "http://localhost:8000/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_urls": [
      "https://etenders.gov.in/eprocure/app",
      "https://gem.gov.in/tenders"
    ]
  }'
```

**Response:**
```json
{
  "job_id": "job_1234567890",
  "status": "processing",
  "message": "Unified RFP workflow started"
}
```

**Save Job ID:**
```bash
JOB_ID=$(curl -s -X POST "http://localhost:8000/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")

echo "Job ID: $JOB_ID"
```

---

### Check Status
```bash
curl "http://localhost:8000/api/status/job_1234567890"
```

**With Job ID Variable:**
```bash
curl "http://localhost:8000/api/status/$JOB_ID" | python3 -m json.tool
```

---

### Get Result
```bash
curl "http://localhost:8000/api/result/job_1234567890"
```

**With Job ID Variable:**
```bash
curl "http://localhost:8000/api/result/$JOB_ID" | python3 -m json.tool
```

---

## 🎨 Output & User Interface Layer

### Approve Response
```bash
curl -X POST "http://localhost:8000/api/response/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_1234567890",
    "approved": true,
    "comments": "Looks good! Ready for submission."
  }'
```

**Reject Example:**
```bash
curl -X POST "http://localhost:8000/api/response/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job_1234567890",
    "approved": false,
    "comments": "Need to revise pricing section"
  }' | python3 -m json.tool
```

---

### Generate PDF
```bash
curl "http://localhost:8000/api/response/generate-pdf/job_1234567890"
```

**With Job ID Variable:**
```bash
curl "http://localhost:8000/api/response/generate-pdf/$JOB_ID" | python3 -m json.tool
```

**Expected Response:**
```json
{
  "status": "ready",
  "job_id": "job_1234567890",
  "pdf_url": "/downloads/job_1234567890.pdf",
  "message": "PDF generation ready (implement PDF library)"
}
```

---

### Job History (Dashboard)
```bash
curl "http://localhost:8000/api/jobs/history?limit=50"
```

**Get Last 10 Jobs:**
```bash
curl "http://localhost:8000/api/jobs/history?limit=10" | python3 -m json.tool
```

---

## 🚀 Complete Test Flow Example

### End-to-End Workflow Test

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. Health Check
echo "1. Checking server health..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

# 2. Start Workflow
echo "2. Starting RFP workflow..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{}')

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"
echo ""

# 3. Check Status (wait a bit)
echo "3. Checking status..."
sleep 2
curl -s "$BASE_URL/api/status/$JOB_ID" | python3 -m json.tool
echo ""

# 4. Test Spec-Match
echo "4. Testing spec-match..."
curl -s -X POST "$BASE_URL/api/spec-match" \
  -H "Content-Type: application/json" \
  -d '{"query": "1.5 sq mm cable", "top_k": 3}' | python3 -m json.tool
echo ""

# 5. Test Pricing
echo "5. Testing pricing..."
curl -s -X POST "$BASE_URL/api/pricing" \
  -H "Content-Type: application/json" \
  -d '{
    "rfp_id": "TEST",
    "technical_table": [{"item_no": 1, "description": "Cable", "quantity": 100}],
    "rfp_summary": {"tests": ["Test"]}
  }' | python3 -m json.tool
echo ""

# 6. Get Result (when ready)
echo "6. Getting result..."
curl -s "$BASE_URL/api/result/$JOB_ID" | python3 -m json.tool
echo ""

echo "✅ Test complete!"
```

---

## 📝 Quick Reference

### All Endpoints at a Glance

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/api/sku-repository` | GET | Get product specs |
| `/api/rfp/scrape` | POST | Scrape RFP portals |
| `/api/historical-responses` | GET | Get past responses |
| `/api/pricing-database` | GET | Get pricing data |
| `/api/spec-match` | POST | Find product matches |
| `/api/pricing` | POST | Calculate costs |
| `/api/process-rfp` | POST | Main workflow |
| `/api/status/{job_id}` | GET | Check status |
| `/api/result/{job_id}` | GET | Get result |
| `/api/response/approve` | POST | Approve/reject |
| `/api/response/generate-pdf/{job_id}` | GET | Generate PDF |
| `/api/jobs/history` | GET | Job history |
| `/docs` | GET | API documentation |

---

## 🛠️ Using the Test Script

**Make executable:**
```bash
chmod +x test_endpoints.sh
```

**Run all tests:**
```bash
./test_endpoints.sh
```

**Or with bash:**
```bash
bash test_endpoints.sh
```

---

## 💡 Tips

1. **Pretty Print JSON**: Always pipe to `python3 -m json.tool` for readable output
2. **Save Job IDs**: Store job_id in a variable for subsequent requests
3. **Check Status**: Poll `/api/status/{job_id}` until status is "completed"
4. **Interactive Testing**: Use http://localhost:8000/docs for GUI testing
5. **Error Handling**: Check HTTP status codes (200 = success, 404 = not found, 500 = error)

---

## 🔍 Troubleshooting

**Server not responding?**
```bash
# Check if server is running
curl http://localhost:8000/

# Check server logs
# Look for errors in terminal where uvicorn is running
```

**Job not found?**
```bash
# List all jobs
curl http://localhost:8000/api/jobs/history
```

**Import errors?**
```bash
# Make sure server is running with venv activated
source venv/bin/activate
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

