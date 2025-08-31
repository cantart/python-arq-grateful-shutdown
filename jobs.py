import asyncio
import logging
from typing import Any, Dict


# Example job functions
async def send_email(ctx: Dict[str, Any], to: str, subject: str, body: str) -> str:
    """
    Example job to send an email.
    In a real application, this would integrate with an email service.
    """
    # Simulate email sending delay
    await asyncio.sleep(2)
    
    result = f"Email sent to {to} with subject '{subject}'"
    logging.info(result)
    return result


async def process_data(ctx: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example job to process some data.
    """
    # Simulate data processing
    await asyncio.sleep(1)
    
    processed_data = {
        "original": data,
        "processed_at": "2025-08-31T00:00:00Z",
        "status": "completed"
    }
    
    logging.info(f"Data processed: {data}")
    return processed_data


async def long_running_task(ctx: Dict[str, Any], duration: int = 10) -> str:
    """
    Example of a long-running task.
    """
    logging.info(f"Starting long running task for {duration} seconds")
    
    for i in range(duration):
        await asyncio.sleep(1)
        logging.info(f"Task progress: {i+1}/{duration}")
    
    result = f"Long running task completed after {duration} seconds"
    logging.info(result)
    return result
