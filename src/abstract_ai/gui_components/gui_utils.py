import os
from abstract_utilities import get_closest_match_from_list
from abstract_utilities.list_utils import ensure_nested_list,find_original_case
from abstract_utilities.class_utils import get_all_functions_for_instance,get_all_params,get_fun
from abstract_gui import make_component,AbstractWindowManager,AbstractBrowser,text_to_key,ensure_nested_list,expandable,RightClickManager,get_screen_dimensions
right_click_mgr=RightClickManager()
def get_standard_screen_dimensions(width=0.70,height=0.80):
    return get_screen_dimensions(width=width,height=height)
window_width,window_height=get_standard_screen_dimensions()
def get_left_right_nav(name,section=True,push=True):
    insert = f"{name} {'section ' if section else ''}"
    nav_bar = [make_component("Button",button_text="<-",key=text_to_key(f"{insert}back"),enable_events=True),
         make_component("input",default_text='0',key=text_to_key(f"{insert}number"),size=(4,1)),
         make_component("Button",button_text="->",key=text_to_key(f"{insert}forward"),enable_events=True)]
    if push:
        nav_bar=[make_component("Push")]+nav_bar+[make_component("Push")]
    return nav_bar
def generate_bool_text(title:str,args:dict={})->object:
    return make_component("Frame",title, layout=[[get_right_click_multi(key=text_to_key(text=title,section='text'),args=args)]],**expandable())
def get_tab_layout(title:str,layout:list=None)->object:
    if not layout:
        layout = get_right_click_multi(key=text_to_key(title),args={**expandable(size=(None, 5))})
    return make_component("Tab",title.upper(),ensure_nested_list(layout))
def get_column(layout:list,args:dict={})->object:
    return make_component("Column",ensure_nested_list(layout),**args)
def get_tab_group(grouped_tabs:list,args:dict={})->object:
    return make_component("TabGroup",ensure_nested_list(grouped_tabs),**args)
def get_right_click_multi(key:str,args:dict={})->object:
    return make_component("Multiline",**args,right_click_menu=right_click_mgr.get_right_click(key=key),key=key)
completion_token_keys = ['completion tokens available','completion tokens desired','completion tokens used']
prompt_token_keys = ['prompt tokens available','prompt tokens desired','prompt tokens used']
chunk_data_keys=['max chunk size','chunk length','chunk total']
all_token_keys = completion_token_keys+prompt_token_keys+chunk_data_keys+['chunk sectioned data']
response_types = ['instruction', 'json', 'bash', 'text']
model_type_keys=['role','response type']
percentage_keys = ['prompt percentage','completion percentage']
file_options_keys = ['auto chunk title','reuse chunk data','append chunks','scan mode all']
test_options_keys = ['test run','test files','test file input','test browse']
instructions_keys = ["instructions","additional_responses","suggestions","abort","database_query","notation","generate_title","additional_instruction","request_chunks","prompt_as_previous","token_adjustment"]
api_keys = ["header",'api key','api env']
