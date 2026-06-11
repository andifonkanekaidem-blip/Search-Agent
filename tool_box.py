from tavily import AsyncTavilyClient
from datetime import datetime,timezone
import httpx
import asyncio
from fastapi import HTTPException
import docker

try:
    docker_client = docker.from_env()
    docker_client.ping()
except Exception as e:
    docker_client = None
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


def run_ai_code(ai_code:str)->str:
    if docker_client is None:
        raise RuntimeError("Docker is Down")

    ai_code = ai_code.replace('"','\\"')
    container = docker_client.containers.run(
        image="run_code_sandbox:latest",
        command=f'python -c "{ai_code}"',
        detach=True,
        network_disabled=True,
        mem_limit="128m",
        nano_cpus=500000000,

    )

    try:
        container.wait(timeout=10)
        logs = container.logs().decode()
        return logs
    except Exception as e:
        raise e
    finally:
        container.stop()
        container.remove()

async def run_code(code:str)->str:
    if docker_client is None:
        raise HTTPException(500)
    try:
        result = await asyncio.to_thread(run_ai_code,code)
        return result.strip()
    except Exception:
        return "Timeout"