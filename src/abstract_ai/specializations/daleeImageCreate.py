from abstract_apis import asyncPostRequest
from abstract_utilities import is_number,os,asyncio
from ..gpt_classes.api_selection import ApiManager
def get_open_image(path):
    try:
        return open(path or os.getcwd(), "rb"),
    except:
        return None
def get_prompt_type(callData={}):
    requestType = "generations"
    if callData.get('mask') == None and callData.get('image'):
        requestType = "variations"
    elif callData.get('image') and callData.get('mask'):
        requestType = "edits"
    return requestType
def trimData(callData):
    if callData.get('mask') == None and 'mask' in callData:
        del callData['mask']
    if callData.get('image') == None and 'image' in callData:
        del callData['image']
    return callData
def get_image_prompt_data(**kwargs):
    prompt = kwargs.get('prompt','')
    quality = kwargs.get('quality',"standard")
    model = kwargs.get('model',"dall-e-3")
    image_item = get_open_image(kwargs.get('image_path'))
    mask_item = get_open_image(kwargs.get('mask_path'))
    size = kwargs.get('size',"1024x1024")
    size = f"{size}x{size}" if 'x' not in size and is_number(size) else size
    n = kwargs.get('n',1)
    n = int(n if is_number(n) and n in range(1,10) else 1)
    call_data = {"quality":quality,"model": model,"image": image_item,"mask": mask_item,"prompt": prompt,"n": n,"size": size}
    return trimData(call_data)
async def call_image_prompt_async(**kwargs):
    api_mgr = kwargs.get('api_mgr') or ApiManager(kwargs.get('apiKey'))
    headers = {"Content-Type": "application/json" , 'Authorization': f"Bearer {api_mgr.api_key}"}
    call_data = get_image_prompt_data(**kwargs)
    requestType = kwargs.get('requestType') or get_prompt_type(call_data)
    return await asyncPostRequest(url=f'https://api.openai.com/v1/images/{requestType}',data=call_data,headers=headers)
def call_image_prompt(*args,**kwargs):
    if args:
        kwargs['prompt']=args[0]
    return asyncio.run(call_image_prompt_async(**kwargs))
