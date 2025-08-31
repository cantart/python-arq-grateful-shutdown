import logging
import asyncio
from arq import create_pool, cron
from arq.connections import RedisSettings
from jobs import send_email, process_data, long_running_task

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


# Example cron job
@cron(hour=0, minute=0)  # Run daily at midnight
async def daily_cleanup(ctx):
    """Example cron job that runs daily"""
    logger.info("Running daily cleanup...")
    await asyncio.sleep(1)
    logger.info("Daily cleanup completed")


class WorkerSettings:
    functions = [
        send_email,
        process_data, 
        long_running_task,
        daily_cleanup,
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
