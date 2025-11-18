# FastAPI Contact API



## Install Required Libraries

```bash
pip install fastapi uvicorn requests
```
or using `uv`:
```bash
uv add fastapi uvicorn requests --link-mode=copy
```

**Requests module documentation:** https://www.w3schools.com/python/module_requests.asp

## Start API Services

Run the API server (`api_server.py`):

```bash
uvicorn api_server:app --reload
```

## Run API Client

Execute the API client (`api_client.py`) to interact with the services.