from tavily import AsyncTavilyClient
from datetime import datetime,timezone
import httpx
async def app_search(tavily_client:AsyncTavilyClient,query:str)->str:
    try:
        result = await tavily_client.search(query, max_results=5,search_depth="basic")
        
        return "\n".join([r["content"] for r in result["results"]])
    except Exception as e:
        return "SEARCH FAILED: No results returned. Do not use training knowledge. Return RejectionSchema immediately."

def get_current_date()->str:
    return datetime.now().strftime("%d %B, %Y")
def get_current_time()->str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")
async def get_weather(location:str)->str:
    geo = await httpx.AsyncClient().get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    )
    coords = geo.json()["results"][0]
    
    weather = await httpx.AsyncClient().get(
        f"https://api.open-meteo.com/v1/forecast?latitude={coords['latitude']}&longitude={coords['longitude']}&current_weather=true"
    )
    return str(weather.json()["current_weather"])

import asyncio
import tempfile
import sys

async def run_code(code):
    # create temp file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(code.encode())
        f.flush()
        path = f.name
    process = await asyncio.create_subprocess_exec(
        "python",
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    return stdout.decode(), stderr.decode()