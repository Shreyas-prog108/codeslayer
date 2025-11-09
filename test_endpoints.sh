#!/bin/bash
# Test Commands for CodeSlayer RFP Automation API
# Run: bash test_endpoints.sh
# Or: chmod +x test_endpoints.sh && ./test_endpoints.sh

BASE_URL="http://localhost:8000"

echo "🧪 Testing CodeSlayer RFP Automation API"
echo "=========================================="
echo ""

# ==================== ROOT ENDPOINT ====================
echo "1️⃣  Testing Root Endpoint (Health Check)"
echo "----------------------------------------"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

# ==================== DATA SOURCES ====================
echo "2️⃣  Testing SKU Repository"
echo "----------------------------------------"
curl -s "$BASE_URL/api/sku-repository?limit=5" | python3 -m json.tool
echo ""
echo ""

echo "3️⃣  Testing RFP Scraping"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/api/rfp/scrape" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""
echo ""

echo "4️⃣  Testing Historical Responses"
echo "----------------------------------------"
curl -s "$BASE_URL/api/historical-responses?limit=10" | python3 -m json.tool
echo ""
echo ""

echo "5️⃣  Testing Pricing Database"
echo "----------------------------------------"
curl -s "$BASE_URL/api/pricing-database" | python3 -m json.tool
echo ""
echo ""

# ==================== SPEC-MATCH TASK ====================
echo "6️⃣  Testing Spec-Match Task (Left Cyan Box)"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/api/spec-match" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "1.5 sq mm cable with high current rating",
    "top_k": 3
  }' | python3 -m json.tool
echo ""
echo ""

# ==================== PRICING TASK ====================
echo "7️⃣  Testing Pricing Task (Right Cyan Box)"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/api/pricing" \
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
  }' | python3 -m json.tool
echo ""
echo ""

# ==================== MAIN WORKFLOW ====================
echo "8️⃣  Testing Main Unified Workflow"
echo "----------------------------------------"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/process-rfp" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "$RESPONSE" | python3 -m json.tool

# Extract job_id for subsequent tests
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', 'no_job_id'))")
echo ""
echo "📌 Job ID: $JOB_ID"
echo ""
echo ""

# ==================== STATUS & RESULTS ====================
if [ "$JOB_ID" != "no_job_id" ]; then
  echo "9️⃣  Testing Status Check"
  echo "----------------------------------------"
  curl -s "$BASE_URL/api/status/$JOB_ID" | python3 -m json.tool
  echo ""
  echo ""

  echo "🔟 Testing Get Result"
  echo "----------------------------------------"
  curl -s "$BASE_URL/api/result/$JOB_ID" | python3 -m json.tool
  echo ""
  echo ""

  # ==================== APPROVAL ====================
  echo "1️⃣1️⃣  Testing Response Approval"
  echo "----------------------------------------"
  curl -s -X POST "$BASE_URL/api/response/approve" \
    -H "Content-Type: application/json" \
    -d "{
      \"job_id\": \"$JOB_ID\",
      \"approved\": true,
      \"comments\": \"Looks good! Ready for submission.\"
    }" | python3 -m json.tool
  echo ""
  echo ""

  echo "1️⃣2️⃣  Testing PDF Generation"
  echo "----------------------------------------"
  curl -s "$BASE_URL/api/response/generate-pdf/$JOB_ID" | python3 -m json.tool
  echo ""
  echo ""
fi

# ==================== JOB HISTORY ====================
echo "1️⃣3️⃣  Testing Job History (Dashboard)"
echo "----------------------------------------"
curl -s "$BASE_URL/api/jobs/history?limit=10" | python3 -m json.tool
echo ""
echo ""

echo "✅ All endpoint tests completed!"
echo ""
echo "📖 For interactive testing, visit: $BASE_URL/docs"

