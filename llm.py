from google.genai import Client,types
from schema import ToolUseSchema,RejectionSchema,SummariseRequest
from tool_box import app_search,get_weather
import json
tools = {
    "search":app_search,
    "weather":get_weather
}
def cleanresponse(resp:str)->str:
    raw_text = resp.strip()
    if raw_text.startswith("```") or raw_text.endswith("```"):
        raw_text = raw_text.strip("`").replace("json\n", "", 1).strip()
    return raw_text

async def get_summary(gemini_client:Client,config:types.GenerateContentConfig,query:str,search_Client,status_func)->dict:
    state = [
        f"User: {query}"
    ]
    await status_func("✅ Validating Input.....")
    for _t in range(10):
        print(f"--- Step {_t+1} ---")
        await status_func("📝 Generating Content...")
        response = await gemini_client.models.generate_content(
            model='gemma-4-31b-it',
            contents=state,
            config=config
            
        )
        
        raw_text = cleanresponse(response.text)
        json_response = json.loads(raw_text)
        if "tool" in json_response:
            if json_response["tool"] in tools:
                print(f"\nAssistant: {json_response["thought"]}\nCalling {json_response["tool"]} tool....")
                print(f"\nTool Query: {json_response["tool_query"]}")
                if json_response["tool"] == 'search':
                    await status_func("🔍 Searching the web...")
                    result = await tools[json_response["tool"]](search_Client,json_response["tool_query"])
                    await status_func("✅ Search Complete")
                elif json_response["tool"] == 'weather':
                    await status_func("🌥️ Getting Weather Information...")
                    result = await tools[json_response["tool"]](json_response["tool_query"])
                    await status_func("✅ Weather Information gotten")
                state.append(f"Assistant: {json_response["thought"]}")
                state.append(f"\nTool Query by Assistant: {json_response["tool_query"]}")
                state.append(f"Tool Response: '{result}'")
                print(f"\nTool response: {result[0:100]}....")
        elif "response" in json_response:
            return json_response
            
        elif "reason" in json_response:
            return json_response
    
