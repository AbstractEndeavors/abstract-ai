from .routes import *
from abstract_utilities import safe_json_loads,eatAll,get_any_value,make_list
from abstract_apis import *

GROK_URL = "https://api.x.ai/v1/chat/completions"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models"
OPENAI_URL = f"https://generativelanguage.googleapis.com/v1beta/models"
URL_SELECT_JS={"openai":OPENAI_URL,"grok":GROK_URL,"gemini":GEMINI_URL}
DEFAULT_HEADERS = {
        "Content-Type": "application/json",
    }
def get_gemini_model(version,typ=None):
    version_types_js={"1.5":["flash"],"2":["flash"],"2.5":['flash','pro']}
    version = str(version or "1.5")
    version_types = version_types_js.get(version)
    if not version_types:
        version = "1.5"
        version_types = version_types_js.get(version)
    if typ not in version_types:
        typ = version_types[0]
    return f"gemini-{version}-{typ}-latest"
def get_api_url(ai=None,typ=None,api_key=None,version=None,version_type=None):
    ai = get_correct_json_key(URL_SELECT_JS,ai)
    url = URL_SELECT_JS.get(ai)
    if ai in ['gemini','GEMINI']:
        model_name = get_gemini_model(version,typ=version_type)
        api_key = api_key or get_ai_api_key(ai=ai,typ=typ)
        url = f"{url}/{model_name}:generateContent?key={api_key}"
    return url
def get_api_header(ai=None,typ=None,api_key=None):
    ai = get_correct_ai_key(ai)
    headers = DEFAULT_HEADERS
    if ai not in ['gemini','GEMINI']:
        api_key = api_key or get_ai_api_key(ai=ai,typ=typ)
        headers["Authorization"]=f"Bearer {api_key}"
    return headers

def get_grok_payload(model=None,role=None,content=None,stream=None,temperature=None):
    content = content or "Testing. Just say hi and hello world and nothing else."
    role= role or "system"
    model = model or "grok-3-latest"
    temperature = temperature or 0
    stream = stream or False
    payload = {}
    payload["messages"]=[{"role": role,"content": content}]
    payload["model"]= model
    payload["stream"]= stream
    payload["temperature"]= temperature
    return payload
def get_gemini_payload(prompt):
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    return data
def get_ai_payload(ai=None,model=None,role=None,content=None,stream=None,temperature=None):
    ai = get_correct_ai_key(ai)
    if ai in ['gemini','GEMINI']:
        payload = get_gemini_payload(prompt = content)
    #if ai in ['grok','GROK']:
    #    payload = get_grok_payload(model=model,role=role,content=content,stream=stream,temperature=temperature)
    return payload
def make_ai_api_call(ai=None,
                     typ=None,
                     api_key=None,
                     version=None,
                     version_type=None,
                     model=None,
                     role=None,
                     prompt=None,
                     stream=False,
                     temperature=None,
                     instructions=None,
                     instruction_bools=None,
                     prompt_data=None,
                     completion_percentage=None,
                     env_path=None,
                     *args,
                     **kwargs):
    ai = get_correct_ai_key(ai)
   
    if ai in ['grok','GROK','openai','OPENAI']:
        api_key = api_key or get_ai_api_key(ai=ai,typ=typ)
        completion_percentage= completion_percentage or 50
        response = make_general_query(prompt=prompt,
                           api_key=api_key,
                           env_path=env_path,
                           completion_percentage=completion_percentage,
                           model=model,
                           instructions=instructions,
                           instruction_bools=instruction_bools,
                           data=prompt_data)
        
        result = get_api_response_value(response)
        
    else:
        headers = get_api_header(ai=ai,typ=typ,api_key=api_key)
        
        payload = get_ai_payload(ai=ai,model=model,role=role,content=prompt,stream=stream,temperature=temperature)
        
        url = get_api_url(ai=ai,typ=typ,api_key=api_key,version=version,version_type=version_type)
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        response = get_response(response)
        
        if ai in ['gemini','GEMINI']:
            #result = response.get('candidates',[{}])[0].get('content',{}).get('parts',[{}])[0].get('text')
            result = make_list(get_any_value(response,'text'))[-1]
        else:
            result = make_list(get_any_value(response,'content'))[-1]
    return result
