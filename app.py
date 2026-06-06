from fastapi import FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from google.genai import Client
from inspect import cleandoc
from writeself import PROMPT
from schema import ResponseSchema,SummariseRequest,ToolUseSchema,RejectionSchema
from typing import Union
from tavily import AsyncTavilyClient
from google.genai.types import GenerateContentConfig
import os
from llm import get_summary
from dotenv import load_dotenv
import uvicorn
import asyncio
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
@asynccontextmanager
async def lifespan(app:FastAPI):
    gemini_client  = Client().aio
    tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    config  = GenerateContentConfig(
        temperature=0.7,
        system_instruction=cleandoc(PROMPT),
        response_mime_type="application/json",
        response_schema=Union[RejectionSchema,ResponseSchema,ToolUseSchema]
    )

    app.state.gemini_client = gemini_client 
    app.state.tavily_client = tavily_client
    app.state.gemini_client_config = config 
    yield
    await gemini_client.aclose() 
    await tavily_client.close()

app =  FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/summarise")
async def web_search(query:SummariseRequest):
    async def generate():  
        queue = asyncio.Queue()
        async def on_status(msg:str):
            await queue.put(msg)
        async def run(): 
            try:
                summary = await get_summary(app.state.gemini_client,app.state.gemini_client_config,query.query,app.state.tavily_client,on_status)
                if "reason" in summary:
                    await on_status(f"REJECT: {summary['reason']}")
                else:
                    await on_status(f"DONE: \n{summary['response']}")
            except Exception as e:
                raise HTTPException(500,detail=str(e))
        asyncio.create_task(run())
        while True:
            msg = await queue.get()
            yield msg+"\n"
            if msg.startswith("DONE:"):
                break
    return StreamingResponse(generate(),media_type='text/plain')

if __name__ == "__main__":

    uvicorn.run("app:app",reload=True)
