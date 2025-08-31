import asyncio
import logging
from typing import Any, Dict, Optional

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ARQ Job Queue API",
    description="API for enqueuing jobs to ARQ Redis queue",
    version="1.0.0"
)

# Redis settings
redis_settings = RedisSettings(
    host='redis',  # Docker service name
    port=6379,
    database=0,
)

# Pydantic models for request/response
class JobRequest(BaseModel):
    function_name: str
    args: list = []
    kwargs: Dict[str, Any] = {}
    delay: Optional[int] = None  # Delay in seconds
    
class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

# Global redis pool
redis_pool = None

@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection pool on startup"""
    global redis_pool
    try:
        redis_pool = await create_pool(redis_settings)
        logger.info("Connected to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Redis connection on shutdown"""
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        logger.info("Redis connection closed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ARQ Job Queue API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint with Redis connectivity"""
    try:
        info = await redis_pool.info()
        return {
            "status": "healthy",
            "redis_connected": True,
            "redis_version": info.get("redis_version", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "redis_connected": False,
            "error": str(e)
        }

@app.post("/jobs/enqueue", response_model=JobResponse)
async def enqueue_job(job_request: JobRequest):
    """
    Enqueue a job to the ARQ queue
    
    Available functions:
    - send_email: args=[to, subject, body]
    - process_data: kwargs={"data": {...}}
    - long_running_task: kwargs={"duration": 10}
    """
    try:
        # Validate function name
        available_functions = ["send_email", "process_data", "long_running_task"]
        if job_request.function_name not in available_functions:
            raise HTTPException(
                status_code=400,
                detail=f"Function '{job_request.function_name}' not available. Available functions: {available_functions}"
            )
        
        # Enqueue the job
        job = await redis_pool.enqueue_job(
            job_request.function_name,
            *job_request.args,
            **job_request.kwargs,
            _defer_by=job_request.delay
        )
        
        logger.info(f"Job {job.job_id} enqueued: {job_request.function_name}")
        
        return JobResponse(
            job_id=job.job_id,
            status="enqueued",
            message=f"Job {job.job_id} has been enqueued successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to enqueue job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")

@app.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status and result of a job"""
    try:
        # Create a Job object to check status
        from arq.jobs import Job
        job = Job(job_id, redis_pool)
        
        # Get job status
        job_status = await job.status()
        
        # Get job result and info if completed
        result = None
        error = None
        
        if job_status.name == "complete":
            try:
                result = await job.result()
            except Exception as e:
                logger.warning(f"Failed to get job result: {e}")
        elif job_status.name == "failed":
            try:
                job_info = await job.info()
                if job_info and hasattr(job_info, 'result'):
                    error = str(job_info.result)
                else:
                    error = "Job failed with unknown error"
            except Exception as e:
                error = f"Job failed: {str(e)}"
        
        return JobStatusResponse(
            job_id=job_id,
            status=job_status.name,
            result=result,
            error=error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/jobs")
async def list_jobs(limit: int = 10):
    """List recent jobs"""
    try:
        # This is a simplified implementation
        # In a real application, you might want to store job metadata separately
        return {
            "message": "Job listing not fully implemented",
            "note": "Use /jobs/{job_id}/status to check specific job status"
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
