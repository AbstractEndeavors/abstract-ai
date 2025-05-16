from .gui_utils import *
def try_title(component:object)->(str or None):
    try:
        while isinstance(component,list):
            component = component[0]
        title = component.Title
    except:
        title=None
    return title
##create_prompt_tab
prompt_tab_keys=['request','prompt data','chunks','query','instructions']
def get_prompt_tabs(layout_specs={},args={}):
    layout = []
    for prompt_tab_key in prompt_tab_keys:
        layout.append(get_tab_layout(prompt_tab_key,layout=layout_specs.get(prompt_tab_key)))
    return get_tab_group(layout,args=args)



def get_prompt_tabs(layout_specs={},args={})->list:
    layout = []
    for prompt_tab_key in prompt_tab_keys:
        layout.append(get_tab_layout(prompt_tab_key,layout=layout_specs.get(prompt_tab_key)))
    return get_tab_group(layout,args=args)          


def get_chunked_sections()->list:
    return [get_left_right_nav(name='chunk'),
            get_left_right_nav(name='chunk',section=False),
            
            [make_component("Frame",
                            f"chunk data",
                            layout=[[get_right_click_multi(key=text_to_key('chunk sectioned data'),
                                                           args={"enable_events":True,**expandable()})]],
                            **expandable())]]
def get_prompt_data_section()->list:
    return [get_left_right_nav(name='prompt_data'),
            [make_component("Frame",
                            'prompt data',
                            layout=[[get_right_click_multi(key=text_to_key('prompt_data data'),
                                                           args={"enable_events":True,**expandable()})]],
                            **expandable())]]
def get_request_section()->list:
    return [get_left_right_nav(name='request'),
            [make_component("Frame","request data",
                            layout=[[get_right_click_multi(key=text_to_key('request'),
                                                           args={"enable_events":True,**expandable()})]],
                            **expandable())]]

def get_query_section()->list:
    return [get_left_right_nav(name='query'),
            get_left_right_nav(name='query',section=False),
            [make_component("Frame",
                            f"query data",
                            layout=[[get_right_click_multi(key=text_to_key('query'),
                                                           args={"enable_events":True,**expandable()})]],
                            **expandable())]]




def get_tab_layout(title,layout=None)->object:
    if not layout:
        layout = [get_left_right_nav(name=title),
                  make_component("Multiline",key=text_to_key(title), **expandable())]
    return make_component("Tab",title.upper(),ensure_nested_list(layout))

def generate_tab(title, layout):
    return make_component("Tab", ensure_nested_list(layout), **expandable())

def get_instructions()->list:
    layout = []
    sub_layout = []
    for instruction_key in instructions_keys:
        if instruction_key == 'instructions':
            layout.append(generate_bool_text(instruction_key, args={**expandable(size=(None, 10))}))
        else:
            component = generate_bool_text(instruction_key, args={**expandable(size=(None, 5))})
            sub_layout.append([component])
    sub_layout = [make_component("Column", ensure_nested_list(sub_layout), **expandable())]
    return [get_left_right_nav(name='instructions'),
        [make_component("Frame",'', layout=[layout, sub_layout])]]
def prompt_tabs():
    layouts = {"query":get_query_section(),
                                  "request":get_request_section(),
                                  "prompt data":get_prompt_data_section(),
                                  "instructions":get_instructions(),
                                  "chunks":get_chunked_sections()}
    return get_prompt_tabs(layouts, args=expandable(size=(int(0.2*window_width),int(window_height))))

