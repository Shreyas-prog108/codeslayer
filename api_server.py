"""
Simple FastAPI server exposing the unified RFP workflow
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn

from unified_workflow import UnifiedRFPWorkflow

app = FastAPI(
    title="CodeSlayer RFP Automation System",
    description="Complete RFP processing workflow with all data sources and task endpoints",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job storage
jobs = {}

# Workflow instance
workflow = UnifiedRFPWorkflow()


class WorkflowRequest(BaseModel):
    rfp_urls: Optional[List[str]] = None

class SpecMatchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class PricingRequest(BaseModel):
    rfp_id: str
    technical_table: List[Dict[str, Any]]
    rfp_summary: Optional[Dict[str, Any]] = {}

class ApprovalRequest(BaseModel):
    job_id: str
    approved: bool
    comments: Optional[str] = ""


@app.get("/")
async def root():
    return {
        "service": "CodeSlayer RFP Automation",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "main_workflow": "/api/process-rfp",
            "data_sources": {
                "sku_repository": "/api/sku-repository",
                "rfp_portals": "/api/rfp/scrape",
                "historical_responses": "/api/historical-responses",
                "pricing_database": "/api/pricing-database"
            },
            "tasks": {
                "spec_match": "/api/spec-match",
                "pricing": "/api/pricing"
            },
            "output": {
                "approve": "/api/response/approve",
                "generate_pdf": "/api/response/generate-pdf"
            }
        }
    }


@app.post("/api/process-rfp")
async def process_rfp(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Main unified endpoint that runs the complete workflow:
    1. Scrape RFPs from sources
    2. Filter and select best RFP
    3. Match products (Spec-Match Task)
    4. Calculate pricing (Pricing Task)
    5. Generate response draft
    
    Returns job_id for tracking
    """
    job_id = f"job_{datetime.now().timestamp()}"
    
    jobs[job_id] = {
        "status": "started",
        "started_at": datetime.utcnow().isoformat(),
        "progress": 0
    }
    
    # Run workflow in background
    background_tasks.add_task(run_workflow, job_id, request.rfp_urls)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Unified RFP workflow started"
    }


def run_workflow(job_id: str, rfp_urls: List[str] = None):
    """Background task to run the workflow"""
    try:
        jobs[job_id]["status"] = "running"
        result = workflow.run(rfp_urls)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        jobs[job_id]["result"] = result
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get workflow status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """Get workflow result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        return {
            "status": job["status"],
            "message": "Workflow not completed yet"
        }
    
    return {
        "status": "completed",
        "result": job.get("result", {})
    }


# ==================== EXTERNAL DATA SOURCES ====================

@app.get("/api/sku-repository")
async def get_sku_repository(limit: int = 100):
    """
    Access SKU Repository - Product specifications database
    """
    try:
        from Technichal_Agent_main.query import load_embeddings
        data = load_embeddings()
        records = data.get("records", [])[:limit]
        return {
            "count": len(records),
            "total_available": data.get("total_records", 0),
            "products": records
        }
    except Exception as e:
        return {
            "count": 0,
            "products": [],
            "note": "SKU repository not available - generate embeddings first"
        }


@app.post("/api/rfp/scrape")
async def scrape_rfp_portals(urls: Optional[List[str]] = None, background_tasks: BackgroundTasks = None):
    """
    Scrape RFPs from tender websites and portals
    """
    from Sales_agent_main.agents.rfp_scraper import scrape_urls
    
    job_id = f"scrape_{datetime.now().timestamp()}"
    jobs[job_id] = {"status": "started", "type": "scraping"}
    
    if urls is None:
        urls = workflow.DEFAULT_URLS
    
    def scrape_task():
        try:
            rfps = scrape_urls(urls)
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["result"] = {"rfps": rfps, "count": len(rfps)}
        except Exception as e:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
    
    background_tasks.add_task(scrape_task)
    
    return {
        "job_id": job_id,
        "status": "scraping",
        "message": f"Scraping {len(urls)} RFP sources"
    }


@app.get("/api/historical-responses")
async def get_historical_responses(limit: int = 50):
    """
    Access historical RFP responses for learning data
    """
    # This would connect to your historical database
    return {
        "count": 0,
        "responses": [],
        "note": "Connect your historical RFP response database here"
    }


@app.get("/api/pricing-database")
async def get_pricing_database():
    """
    Access pricing and test cost database
    """
    try:
        from pricing_agent.load_data import load_reference_data
        product_df, test_df = load_reference_data("pricing_agent/Pricing_Data_FMCG.xlsx")
        return {
            "products_count": len(product_df),
            "tests_count": len(test_df),
            "status": "available"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ==================== SPEC-MATCH TASK (Left Cyan Box) ====================

@app.post("/api/spec-match")
async def trigger_spec_match(request: SpecMatchRequest):
    """
    Trigger Spec-Match Task - Find matching products from SKU repository
    """
    try:
        from Technichal_Agent_main.query import search_cables
        
        results = search_cables(request.query, top_k=request.top_k)
        
        matches = []
        for score, record in results:
            matches.append({
                "match_score": float(score),
                "product": {
                    "conductor_area_mm2": record.get('conductor_nominal_area_mm2'),
                    "current_rating_amps": record.get('current_rating_amps'),
                    "diameter_mm": record.get('approx_overall_diameter_mm'),
                    "weight_kg_per_km": record.get('overall_weight_kg_per_km'),
                }
            })
        
        return {
            "query": request.query,
            "matches_count": len(matches),
            "top_3_matches": matches[:3],
            "all_matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spec-match error: {str(e)}")


# ==================== PRICING TASK (Right Cyan Box) ====================

@app.post("/api/pricing")
async def trigger_pricing(request: PricingRequest):
    """
    Trigger Pricing Task - Calculate pricing table and test costs
    """
    try:
        from pricing_agent.pricing_agent import run_pricing_agent
        
        pricing_input = {
            "rfp_id": request.rfp_id,
            "technical_table": request.technical_table,
            "rfp_summary": request.rfp_summary
        }
        
        result = run_pricing_agent(pricing_input)
        
        return {
            "rfp_id": request.rfp_id,
            "total_material_cost": result.get("total_material_cost", 0),
            "total_test_cost": result.get("total_test_cost", 0),
            "grand_total": result.get("grand_total", 0),
            "pricing_table": result.get("pricing_table", []),
            "test_breakdown": result.get("test_breakdown", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pricing error: {str(e)}")


# ==================== OUTPUT & USER INTERFACE LAYER ====================

@app.post("/api/response/approve")
async def approve_response(request: ApprovalRequest):
    """
    Human Review and Approval - Approve or reject generated RFP response
    """
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    jobs[request.job_id]["approved"] = request.approved
    jobs[request.job_id]["approval_comments"] = request.comments
    jobs[request.job_id]["approved_at"] = datetime.utcnow().isoformat()
    
    if request.approved:
        return {
            "status": "approved",
            "message": "RFP response approved and ready for submission",
            "job_id": request.job_id
        }
    else:
        return {
            "status": "rejected",
            "message": "RFP response rejected",
            "comments": request.comments,
            "job_id": request.job_id
        }


@app.get("/api/response/generate-pdf/{job_id}")
async def generate_pdf_response(job_id: str):
    """
    Generate Final RFP Response as PDF for submission
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if not job.get("approved"):
        raise HTTPException(status_code=400, detail="Response not approved yet")
    
    # PDF generation would go here
    return {
        "status": "ready",
        "job_id": job_id,
        "pdf_url": f"/downloads/{job_id}.pdf",
        "message": "PDF generation ready (implement PDF library)"
    }


@app.get("/api/jobs/history")
async def get_job_history(limit: int = 50):
    """
    Get processing history for dashboard
    """
    history = list(jobs.values())[-limit:]
    return {
        "count": len(history),
        "jobs": history
    }


if __name__ == "__main__":
    print("\n🚀 Starting CodeSlayer RFP Automation API Server...")
    print("📍 Main Workflow: http://localhost:8000/api/process-rfp")
    print("📍 Spec-Match Task: http://localhost:8000/api/spec-match")
    print("📍 Pricing Task: http://localhost:8000/api/pricing")
    print("📖 Docs: http://localhost:8000/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

