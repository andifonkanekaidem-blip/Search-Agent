from tavily import AsyncTavilyClient
from datetime import datetime,timezone
import httpx
import asyncio
from fastapi import HTTPException
import builtins
import io

allowed_imports = {"sympy", "numpy", "math"}

async def app_search(tavily_client:AsyncTavilyClient,query:str)->str:
    try:
        result = await tavily_client.search(query, max_results=5,search_depth="basic")
        
        return "\n".join([r["content"] for r in result["results"]])
    except Exception as e:
        return "SEARCH FAILED: No results returned. Do not use training knowledge. Return RejectionSchema immediately."

async def get_weather(location:str)->str:
    geo = await httpx.AsyncClient().get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    )
    coords = geo.json()["results"][0]
    
    weather = await httpx.AsyncClient().get(
        f"https://api.open-meteo.com/v1/forecast?latitude={coords['latitude']}&longitude={coords['longitude']}&current_weather=true"
    )
    return str(weather.json()["current_weather"])


async def run_code(code:str)->str:
    
    global allowed_imports
    try:

        local_vars = {}
        stdout_capture = io.StringIO()
        def safe_import(name, *args, **kwargs):
            if name not in allowed_imports:
                raise ImportError(f"Import of '{name}' is not allowed")
            return builtins.__import__(name, *args, **kwargs)
        safe_builtins = vars(builtins).copy()
        safe_builtins["__import__"] = safe_import
        exec(code, {"__builtins__": safe_builtins, "__import__": safe_import,"print": lambda *args, **kwargs: print(*args, **kwargs, file=stdout_capture)}, local_vars)
        output = stdout_capture.getvalue().strip()
        return output or str(local_vars.get("result", local_vars))
    except Exception as e:
        return f"Error: {str(e)}"