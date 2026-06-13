from google.genai import Client,types
from tool_box import app_search,get_weather,run_code
import json
tools = {
    "search":app_search,
    "weather":get_weather,
    "code_exec":run_code
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
    await status_func("✅ Validating Input.....||END||")
    for _ in range(10):
        await status_func("📝 Generating Content...||END||")
        response = await gemini_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=state,
            config=config
            
        )
        raw_text = cleanresponse(response.text)
        json_response = json.loads(raw_text)
        if "tool" in json_response:
            if json_response["tool"] in tools:
                if json_response["tool"] == 'search':
                    await status_func("🔍 Searching the web...||END||")
                    result = await tools[json_response["tool"]](search_Client,json_response["tool_query"])
                    await status_func("✅ Search Complete||END||")
                elif json_response["tool"] == 'weather':
                    await status_func("🌥️ Getting Weather Information...||END||")
                    result = await tools[json_response["tool"]](json_response["tool_query"])
                    await status_func("✅ Weather Information gotten||END||")
                elif json_response["tool"] == 'code_exec':
                    await status_func("🧮 Calculating...||END||")
                    result = await tools[json_response["tool"]](json_response["tool_query"])
                    await status_func("✅ Calculation complete||END||")
                state.append(f"Assistant: {json_response['thought']}")
                state.append(f"\nTool Query by Assistant: {json_response['tool_query']}")
                state.append(f"Tool Response: '{result}'")
        elif "response" in json_response:
            return json_response
            
        elif "reason" in json_response:
            return json_response
    
