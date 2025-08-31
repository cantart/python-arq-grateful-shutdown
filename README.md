# ARQ Job Queue with FastAPI

This project demonstrates how to use ARQ (Async Redis Queue) with FastAPI to create a job queue system with a REST API.

## Features

- **FastAPI REST API** for enqueuing jobs
- **ARQ Worker** for processing jobs asynchronously  
- **Redis** as the message broker
- **Docker Compose** for easy deployment
- **Health checks** for monitoring

## Project Structure

```
.
├── api.py                 # FastAPI application with job endpoints
├── worker.py             # ARQ worker configuration
├── jobs.py               # Job function definitions
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker composition
├── Dockerfile.api        # API container image
├── Dockerfile.worker     # Worker container image
└── README.md            # This file
```

## Available Job Functions

1. **send_email** - Simulates sending an email
   - Args: `[to, subject, body]`
   
2. **process_data** - Processes arbitrary data
   - Kwargs: `{"data": {...}}`
   
3. **long_running_task** - Simulates a long-running task
   - Kwargs: `{"duration": 10}` (seconds)

## Quick Start

### Using Docker Compose (Recommended)

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Check if services are running:
   ```bash
   docker-compose ps
   ```

3. View logs:
   ```bash
   # API logs
   docker-compose logs api
   
   # Worker logs  
   docker-compose logs worker
   
   # All logs
   docker-compose logs -f
   ```

### Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis:
   ```bash
   redis-server
   ```

3. Start the worker:
   ```bash
   arq worker.WorkerSettings
   ```

4. Start the API (in another terminal):
   ```bash
   uvicorn api:app --reload
   ```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Enqueue a Job
```bash
# Send email job
curl -X POST "http://localhost:8000/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "send_email",
    "args": ["user@example.com", "Hello", "This is a test email"]
  }'

# Process data job
curl -X POST "http://localhost:8000/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "process_data",
    "kwargs": {
      "data": {"name": "John", "age": 30}
    }
  }'

# Long running task with delay
curl -X POST "http://localhost:8000/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "function_name": "long_running_task",
    "kwargs": {"duration": 5},
    "delay": 10
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/jobs/{job_id}/status
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check with Redis connectivity
- `POST /jobs/enqueue` - Enqueue a new job
- `GET /jobs/{job_id}/status` - Get job status and result
- `GET /jobs` - List jobs (placeholder)

## Configuration

### Redis Settings
Both API and worker connect to Redis using these settings:
- Host: `redis` (Docker service name) or `localhost` (local development)
- Port: `6379`
- Database: `0`

### Worker Settings
- Max jobs: `10`
- Job timeout: `300` seconds (5 minutes)
- Keep result: `3600` seconds (1 hour)
- Queue name: `arq:queue`

## Development

### Adding New Job Functions

1. Define your job function in `jobs.py`:
   ```python
   async def my_new_job(ctx, arg1: str, arg2: int = 10):
       # Your job logic here
       return {"result": "success"}
   ```

2. Add it to the worker's function list in `worker.py`:
   ```python
   class WorkerSettings:
       functions = [
           send_email,
           process_data,
           long_running_task,
           my_new_job,  # Add your function here
       ]
   ```

3. Update the available functions list in `api.py`:
   ```python
   available_functions = ["send_email", "process_data", "long_running_task", "my_new_job"]
   ```

### Monitoring

- View API documentation: http://localhost:8000/docs
- Monitor Redis: Use redis-cli or a Redis GUI tool
- Worker logs show job processing status

## Stopping Services

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Troubleshooting

1. **Connection refused errors**: Make sure Redis is running
2. **Import errors**: Check that all dependencies are installed
3. **Worker not processing jobs**: Check worker logs and Redis connectivity
4. **API not responding**: Check if the API container is running and port 8000 is available
