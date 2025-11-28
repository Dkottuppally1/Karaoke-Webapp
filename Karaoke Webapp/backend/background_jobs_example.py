"""
Example: Background Job Architecture for Karaoke Separation

This is a reference implementation showing how to convert the blocking
separation endpoint into a non-blocking background job system.

To use this:
1. Copy the relevant parts into app.py
2. Update frontend to use /api/separate/start and polling
3. Consider using Redis/database for job storage in production
"""

from fastapi import FastAPI, BackgroundTasks, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Dict
from pathlib import Path

from separation_engine import separate_audio, setup_model

app = FastAPI()

# Simple in-memory job store (for dev - use Redis/DB in production)
JOBS: Dict[str, Dict] = {}

# Global model instance
model = None

def run_separation_job(job_id: str, file_path: str, output_dir: str):
    """
    Background task that runs the separation
    """
    global model
    try:
        # Update job status
        JOBS[job_id]["status"] = "running"
        
        # Run separation
        result = separate_audio(
            model=model,
            input_path=file_path,
            output_dir=output_dir
        )
        
        # Mark as done and store result
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["result"] = result
        
        # Clean up input file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        print(f"Job {job_id} failed: {e}")

@app.post("/api/separate/start")
async def start_separation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Start a separation job (non-blocking)
    Returns job_id immediately
    """
    global model
    
    # Validate file type
    allowed_extensions = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file to temporary location
    tmp_dir = Path("tmp_inputs")
    tmp_dir.mkdir(exist_ok=True)
    
    input_path = tmp_dir / f"{uuid.uuid4()}{file_ext}"
    
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Check file size
    file_size = input_path.stat().st_size
    if file_size > 50 * 1024 * 1024:
        input_path.unlink()
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size: 50MB"
        )
    
    # Create job
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "pending",
        "result": None,
        "error": None,
    }
    
    # Queue background task
    output_dir = "outputs"
    background_tasks.add_task(
        run_separation_job,
        job_id,
        str(input_path),
        output_dir
    )
    
    # Return immediately
    return JSONResponse({
        "job_id": job_id,
        "status": "pending",
        "message": "Separation job started"
    })

@app.get("/api/separate/status/{job_id}")
async def get_separation_status(job_id: str):
    """
    Check the status of a separation job
    """
    job = JOBS.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job_id,
        "status": job["status"]
    }
    
    if job["status"] == "done":
        result = job["result"]
        response["files"] = {
            "instrumental": f"/api/download/{result['instrumental_id']}",
            "vocals": f"/api/download/{result['vocals_id']}",
            "original": f"/api/download/{result['original_id']}"
        }
        response["metadata"] = result.get("metadata", {})
    elif job["status"] == "error":
        response["error"] = job["error"]
    
    return JSONResponse(response)

# Frontend polling example (JavaScript):
"""
// Start separation
const startResponse = await axios.post('/api/separate/start', formData);
const { job_id } = startResponse.data;

// Poll for status
const pollStatus = async () => {
  const statusResponse = await axios.get(`/api/separate/status/${job_id}`);
  const { status, files, error } = statusResponse.data;
  
  if (status === 'done') {
    // Show results
    setResult({ files, metadata: statusResponse.data.metadata });
  } else if (status === 'error') {
    setError(error);
  } else {
    // Still processing - poll again in 2 seconds
    setTimeout(pollStatus, 2000);
  }
};

pollStatus();
"""

