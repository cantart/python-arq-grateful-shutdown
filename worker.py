import asyncio
import logging

from arq import cron, func
from arq.connections import RedisSettings

from jobs import long_running_task, process_data, send_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def startup(ctx):
    """Called when the worker starts"""
    logger.info("Worker starting up...")


async def shutdown(ctx):
    """Called when the worker shuts down"""
    logger.info("Worker shutting down...")


# Example cron job function
async def daily_cleanup(ctx):
    """Example cron job that runs daily at midnight"""
    logger.info("Running daily cleanup...")
    await asyncio.sleep(1)
    logger.info("Daily cleanup completed")


class WorkerSettings:
    # Per-job timeouts via arq.func wrapper
    functions = [
        func(send_email, timeout=15),        # short I/O
        func(process_data, timeout=60),      # medium CPU/IO
        func(long_running_task, timeout=300) # long tasks
    ]
    
    # Cron jobs configuration
    cron_jobs = [
        cron(daily_cleanup, hour=0, minute=0),  # Run daily at midnight
    ]
    
    on_startup = startup
    on_shutdown = shutdown
    
    # Redis settings
    redis_settings = RedisSettings(
        host='redis',  # Docker service name
        port=6379,
        database=0,
    )
    
    # Worker settings
    queue_name = 'arq:queue'
    max_jobs = 10
    job_timeout = 300  # 5 minutes
    keep_result = 3600  # Keep results for 1 hour
    job_completion_wait = 30  # seconds
    # Allow jobs to be aborted via Job.abort (API cancel endpoint)
    allow_abort_jobs = True
