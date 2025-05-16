from ..api_selection import ApiManager
from ..model_selection import ModelManager
from ..prompt_selection import PromptManager
from ..instruction_selection import InstructionManager
from ..response_selection import ResponseManager
from abstract_apis import get_async_response
import asyncio
async def get_query(response_mgr):
    return await response_mgr.initial_query()
async def async_make_general_query(prompt=None,
                                   api_key=None,
                                   env_path=None,
                                   completion_percentage=50,
                                   model=None,
                                   instructions={},
                                   instruction_bools={},
                                   data=None):
    api_mgr = ApiManager(api_key=api_key, env_path=env_path)
    model_mgr = ModelManager(input_model_name=model)
    inst_mgr = InstructionManager(instructions=instructions, instruction_bools=instruction_bools)
    prompt_mgr = PromptManager(request_data=prompt, prompt_data=data, completion_percentage=completion_percentage, instruction_mgr=inst_mgr, model_mgr=model_mgr)
    response_mgr = ResponseManager(prompt_mgr=prompt_mgr, api_mgr=api_mgr)
    # Await the query directly
    return await get_query(response_mgr)
def make_general_query(prompt=None, api_key=None, env_path=None, completion_percentage=50, model=None, instructions=None, instruction_bools=None, data=None):
    return get_async_response(
        async_make_general_query,
        prompt=prompt,
        api_key=api_key,
        env_path=env_path,
        completion_percentage=completion_percentage,
        model=model,
        instructions=instructions,
        instruction_bools=instruction_bools,
        data=data
    )
