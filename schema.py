from pydantic import BaseModel,Field
from typing import Literal

class ToolUseSchema(BaseModel):
    tool:Literal['search','weather']
    thought:str = Field(...,description="Here you place your thought process")
    tool_query:str = Field(None,description="This is where you place the search query or city location.")

class ResponseSchema(BaseModel):
    response:str = Field(...,description="Put the answer to the question here")
class RejectionSchema(BaseModel):
    reason:str = Field(...,description="This is where you write the brief rejection note prompting it to be explicit")
class SummariseRequest(BaseModel):
    query:str