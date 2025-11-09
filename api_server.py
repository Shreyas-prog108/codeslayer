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
    title="CodeSlayer RFP Automation - Unified Endpoint",
    description="Single endpoint for complete RFP processing workflow",
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


@app.get("/")
async def root():
    return {
        "service": "CodeSlayer RFP Automation",
        "status": "online",
        "version": "1.0.0",
        "endpoint": "/api/process-rfp"
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


if __name__ == "__main__":
    print("\n🚀 Starting CodeSlayer RFP Automation API Server...")
    print("📍 Unified endpoint: http://localhost:8000/api/process-rfp")
    print("📖 Docs: http://localhost:8000/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

