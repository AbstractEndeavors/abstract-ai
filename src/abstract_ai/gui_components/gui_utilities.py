from .gui_utils import *
from ..gpt_classes import ModelManager as modelInfoManager

def make_default_checkbox(title:str,default:bool=True)->object:
    return make_component("Checkbox",title,key=text_to_key(text=title,section='bool'),enable_events=True,default=default)
all_models = modelInfoManager().all_model_names
def get_tokens_by_model(model_name:str)->int:
    return modelInfoManager()._get_max_tokens_by_model(model_name)
def get_table_names(*args,**kwargs):
    return []
def get_num_list()->list:
    num_list=[5]
    while num_list[-1] < 95:
        num_list.append(num_list[-1]+1)
    return num_list
def roles_js()->dict:
    return {'assistant':'you are an assistant','Elaborative': 'The model provides detailed answers, expanding on the context or background of the information. E.g., "What is the capital of France?" Answer', 'Socratic': 'The model guides the user to the answer through a series of questions, encouraging them to think critically.', 'Concise': 'The model provides the shortest possible answer to a question.', 'Friendly/Conversational': 'The model interacts in a more relaxed, friendly manner, possibly using casual language or even humor.', 'Professional/Formal': 'The model adopts a formal tone, suitable for professional settings.', 'Role-Playing': 'The model assumes a specific character or role based on user instructions. E.g., "You\'re a medieval historian. Tell me about castles."', 'Teaching': 'The model provides step-by-step explanations or breakdowns, as if teaching a concept to someone unfamiliar with it.', "Debative/Devil's Advocate": 'The model takes a contrarian view to encourage debate or show alternative perspectives.', 'Creative/Brainstorming': 'The model generates creative ideas or brainstorming suggestions for a given prompt.', 'Empathetic/Supportive': 'The model offers emotional support or empathy, being careful not to provide medical or psychological advice without proper disclaimers.'}

def roles_keys()->list:
    return list(roles_js().keys())

def content_type_list()->list:
    return ['application/json','text/plain', 'text/html', 'text/css', 'application/javascript',  'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp', 'audio/mpeg', 'video/mp4', 'video/webm', 'audio/ogg', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/octet-stream', 'application/zip', 'multipart/form-data', 'application/x-www-form-urlencoded', 'font/woff', 'font/woff2', 'font/ttf', 'font/otf', 'application/wasm', 'application/manifest+json', 'application/push-options+json']

def get_settings()->list:
    def get_tokens_layout()->list:
        def get_tokens_display()->list:
            return [
                [get_tokens_section(create_token_section(completion_token_keys,0.5,[8200,8200,0]))],
                [get_tokens_section(create_token_section(prompt_token_keys,0.5,[8200,8200,0]))],
                [get_tokens_section(create_token_section(chunk_data_keys,0.5,[8200,0,0]))]
                ]
        
        def get_tokens_section(tokens_dict)->object:
            layout = []
            for title,default_value in tokens_dict.items():
                frame_title = title.split(' ')[0]
                layout.append(make_component("Text",f'{title.split(" ")[-1]}:', auto_size_text=True))
                layout.append(make_component("Input",key=text_to_key(text=title), default_text=default_value,size=(10,1), readonly=True,enable_events=True))
            return make_component("Frame",frame_title,layout=[layout])
        
        def create_token_section(keys,percentage,values)->list:
            section={}
            for i,key in enumerate(keys):
                section[key]=int(values[i]*percentage)
            return section
        return [make_component("Column",get_tokens_display())]
    
    ##percentage selection
    def get_percentage_component()->list:
        layout = []
        for key in percentage_keys:
            layout.append(make_component("Column",ensure_nested_list(make_component("Frame",f'{key[:4]} %',layout=ensure_nested_list(make_component("Combo",values=get_num_list(), default_value=50, key=text_to_key(text=key), enable_events=True))))))
        return layout
    
    def make_file_options_checks(keys:list)->list:
        layout = []
        for key in keys:
            layout.append(make_component("Checkbox",key,default=True,key=text_to_key(key), enable_events=True))
        return layout
    
    def make_test_options_component()->list:
        layout=[]
        for i,component_name in enumerate(["Checkbox","Checkbox","Input","FilesBrowse"]):
            if component_name == 'Checkbox':
                component =make_component(component_name,test_options_keys[i],default=False,key=text_to_key(text=test_options_keys[i]), enable_events=True)
            else:
                component =make_component(component_name,default=False,key=text_to_key(text=test_options_keys[i]), enable_events=True)
            layout.append(component)
        return layout
    
    def generate_instructions_bool(instruction_key_list:list)->list:
        layout = [[]]
        for i,instruction in enumerate(instruction_key_list):
            if i%4==float(0) and i != 0:
                layout.append([])
            default=False
            if instruction in ['instructions','generate_title','suggestions']:
                default=True
            layout[-1].append(make_default_checkbox(instruction,default=default))
        return layout
    
    def get_api_options_component()->list:
        layout=[]
        for key in api_keys:   
            layout.append([make_component("Frame",key,ensure_nested_list(make_component("Input",key=text_to_key(text=key), enable_events=True)))])
        return layout
    
    def get_type_options_component()->list:
        layout=[]
        roles = list(roles_js().keys())
        response_types = ['instruction', 'json', 'bash', 'text']
        values_list= [roles,response_types]
        for i,key in enumerate(model_type_keys):     
            layout.append(make_component("Combo",values=values_list[i], default_value=values_list[i][0], key=text_to_key(text=key), enable_events=True))
        return layout
    
    ### model selection
    def get_model_selection_layout():
        def get_endpoint_selector()->object:
            return make_component("Frame",'Endpoint',[[make_component("Input",key='-ENDPOINT-', readonly=True, enable_events=True,disabled=True)]])
        def get_model_selector()->object:
            return make_component("Frame",'Model',[[make_component("Combo",all_models, default_value=all_models[0], key='-MODEL-', enable_events=True)]])
        def get_token_display()->object:
            return make_component("Frame",'tokens',[[make_component("Input",get_tokens_by_model(all_models[0]),key='-MAX_TOKENS-', readonly=True, enable_events=True,disabled=True,size=(5,1))]])
        return [[get_endpoint_selector()], [get_model_selector(),get_token_display()]]
    
    def prompt_options_component()->list:
        return make_file_options_checks(['prompt as recieved'])
    num_list=[5]
    while num_list[-1] < 95:
        num_list.append(num_list[-1]+5)

    title_bool=make_component("Checkbox",'Title', key=text_to_key("title bool",section="bool"), auto_size_text=True, enable_events=True)
    title_input=make_component("input",key=text_to_key("title text"), enable_events=True)
    instruction_checkboxes=ensure_nested_list(generate_instructions_bool(instructions_keys))
    file_options = ensure_nested_list(make_file_options_checks(file_options_keys))
    test_options= ensure_nested_list(make_test_options_component())
    return [
            [make_component("Frame",'Token Percentage',ensure_nested_list(get_percentage_component()))],
            [make_component("Frame",'Api Options',ensure_nested_list(get_api_options_component()))],
            [make_component("Frame",'Type Options',ensure_nested_list(get_type_options_component()))],
            [make_component("Frame",'prompt options',ensure_nested_list(prompt_options_component()))],
            [make_component("Frame",'Tokens',ensure_nested_list(get_tokens_layout()))],
            [make_component("Frame",'Title',ensure_nested_list([title_bool,title_input]))],
            
            [make_component("Frame","model select",ensure_nested_list(get_model_selection_layout()))],
            [make_component("Frame","enable instruction", ensure_nested_list(instruction_checkboxes))],
            [make_component("Frame","Test Tools", ensure_nested_list(test_options))],
            [make_component("Frame","file options", ensure_nested_list(file_options))]
        ]

def get_json_tree()->list:
    return [[make_component("Tree",
        data=make_component("TreeData"),
        headings=['Value'],
        auto_size_columns=True,
        num_rows=20,
        col0_width=40,
        key='-JSON-TREE-',
        show_expanded=False,)]]
    
def get_right_click_multi(key:str,args:dict={})->object:
    return make_component("Multiline",**args,right_click_menu=right_click_mgr.get_right_click(key=key),key=key)

def get_response()->object:
    output_layout = get_right_click_multi(key=text_to_key(text='response'),args={**expandable()})
    return make_component("Frame",'Response',layout=[[output_layout]], **expandable())

def get_feedback()->list:
    layout = [get_response()]
    sub_sub_layout = []
    sub_layout = []
    for i,title in enumerate(["request_chunks",'abort','additional_responses','suggestions', 'notation','other']):
        if title in ["request_chunks",'abort','additional_responses']:
            component = make_component("Input",key=text_to_key(text=title,section='feedback'),size=(None, 1))
            sub_sub_layout.append(make_component('Frame',title, layout=[[component]]))
        else:
            component = get_right_click_multi(key=text_to_key(text=title,section='feedback'),args={**expandable()})
            sub_layout.append([make_component('Frame',title, layout=[[component]],**expandable())])
    sub_layout = [make_component("Column", ensure_nested_list([sub_sub_layout]+sub_layout), **expandable(scroll_vertical=True))]
    return [layout,sub_layout]

def get_response_json_info()->object:
    data = {'id': 38, 'object': 15, 'created': 1699622029, 'model': 10, 'usage': 3, 'file_path': 144, 'title': 'Misunderstood input'}
    layout = [[]]
    file_path = []
    for key,value in data.items():
        component = make_component("Frame",str(key),ensure_nested_list(make_component('Input',value,key=text_to_key(key,section='response_output'),size=(value,1))))
        if key == 'file_path':
            file_path.append([make_component('Button',"OPEN",key='-OPEN_RESPONSE-',enable_events=True),component])
        else:
            layout[-1].append(component)
    layout.append(file_path)
    return make_component("Frame",ensure_nested_list(layout))
def database_browser_layout(section='database',extra_component=None):
    database_query=make_component("Checkbox",'database query', key=text_to_key("DATABASE_QUERY_BOOL",section=section), enable_events=True)
    perform_query=make_component("Checkbox",'perform query', key=text_to_key("PERFORM_QUERY_BOOL",section=section), enable_events=True)
    table_configuration=make_component("Frame",'table configuration',layout=ensure_nested_list(make_component("Combo",get_table_names(), size=(15,1),key=text_to_key("chunk title",section=section), enable_events=True)))
    query_component_files = [make_component('Column',ensure_nested_list([[database_query],[perform_query]])),make_component('Column',ensure_nested_list(table_configuration))]
    chunk_data_buttons = make_component('Column',ensure_nested_list([[make_component("Button",'CHUNK_DATA',key=text_to_key(text='add file to chunk',section=section),enable_events=True),
                     make_component("Button",'RESPONSE_DATA',key=text_to_key(text='add file to response',section=section),enable_events=True)]]))
    
    extra_buttons = [chunk_data_buttons]
    
    extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(query_component_files))))
    extra_buttons.append(extra_frame)
    return AbstractBrowser().get_scan_browser_layout(section=section,extra_buttons=extra_buttons)+[[get_right_click_multi(key=text_to_key('file text',section=section),args={**expandable()})]]

def response_browser_layout(section='responses',extra_component=None):
    collate_responses=make_component("Checkbox",'Collate Responses', key=text_to_key("COLLATE_BOOL",section=section), enable_events=True)
    json_to_string=make_component("Checkbox",'Json to String', key=text_to_key("FORMAT_JSON_TO_STRING",section=section), enable_events=True)
    key_selection=make_component("Frame",'response key',layout=ensure_nested_list(make_component("Combo",[], size=(15,1),key=text_to_key("response key selection",section=section), enable_events=True)))
    extra_component_responses = [make_component('Column',ensure_nested_list([[collate_responses],[json_to_string]])),make_component('Column',ensure_nested_list(key_selection))]
    extra_buttons = []
    if extra_component != None:
        extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(extra_component))))
        extra_buttons.append(extra_frame)
    return AbstractBrowser().get_scan_browser_layout(section=section,extra_buttons=extra_component_responses)+[[get_right_click_multi(key=text_to_key('file text',section=section),args={**expandable()})]]


def file_browser_layout(section='files',extra_component=None):
    inputs = make_component("Input",key=text_to_key("chunk title",section=section),size=(15,1))
    frames = make_component("Frame",'chunk title',layout=ensure_nested_list(inputs))
    chunk_title = make_component('Column',ensure_nested_list(frames))
    chunk_data_buttons = make_component('Column',ensure_nested_list([[make_component("Button",'CHUNK_DATA',key=text_to_key(text='add file to chunk',section=section),enable_events=True),
                     make_component("Button",'RESPONSE_DATA',key=text_to_key(text='add file to response',section=section),enable_events=True)]]))
    
    extra_buttons = [chunk_data_buttons,chunk_title]
    if extra_component != None:
        extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(extra_component))))
        extra_buttons.append(extra_frame)
    return AbstractBrowser().get_scan_browser_layout(section=section,extra_buttons=extra_buttons)+[[get_right_click_multi(key=text_to_key('file text',section=section),args={**expandable()})]]

def utilities()->list:
    layout = []
    format_json=make_component("Checkbox",'format json',default = True,key=text_to_key("format json to string",section='responses'), enable_events=True)
    layout.append(make_component("Tab",'SETTINGS', ensure_nested_list(make_component("Column",get_settings(),**expandable(scroll_vertical=True,scroll_horizontal=True))),**expandable(scroll_horizontal=True))),
    layout.append(make_component("Tab",'RESPONSES', response_browser_layout(),key=text_to_key(text='response tab'),**expandable())),
    layout.append(make_component("Tab",'Files', file_browser_layout(),key=text_to_key(text='file tab'),**expandable())),
    layout.append(make_component("Tab",'QUERY', database_browser_layout(),key=text_to_key(text='query tab'),**expandable())),
    layout.append(make_component("Tab",'urls', get_urls(),key=text_to_key(text='url tab'),**expandable())),
    layout.append(make_component("Tab",'feedback', get_feedback(),**expandable(),key=text_to_key(text='feedback tab')))
    return  make_component("TabGroup",ensure_nested_list(layout),**expandable(size=(int(0.4*window_width),int(window_height))))

def get_urls()->list:
    return [
        [make_component("Input",key='-URL-', enable_events=True), make_component("Button",'Add URL',key='-ADD_URL-',enable_events=True), make_component("Listbox",values=[], key='-URL_LIST-', size=(70, 6))],
        [make_component("Button",'GET SOUP',key=text_to_key(text='get soup'),enable_events=True),
         make_component("Button",'GET SOURCE',key=text_to_key(text='get source code'),enable_events=True),
         make_component("Button",'CHUNK_DATA',key=text_to_key(text='add url to chunk'),enable_events=True),
         make_component("Frame",'chunk title',layout=[[make_component("Input",key=text_to_key(text='chunk title',section='url'),size=(20,1))]])],
        [get_right_click_multi(key=text_to_key('url text'),args={**expandable()})]
    ]

def abstract_browser_layout(section=None,extra_component=None):
    inputs = make_component("Input",key=text_to_key("chunk title",section=section),size=(15,1))
    frames = make_component("Frame",'chunk title',layout=ensure_nested_list(inputs))
    chunk_title = make_component('Column',ensure_nested_list(frames))
    chunk_data_buttons = make_component('Column',ensure_nested_list([[make_component("Button",'CHUNK_DATA',key=text_to_key(text='add file to chunk',section=section),enable_events=True),
                     make_component("Button",'RESPONSE_DATA',key=text_to_key(text='add file to response',section=section),enable_events=True)]]))
    
    extra_buttons = [chunk_data_buttons,chunk_title]
    if extra_component != None:
        extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(extra_component))))
        extra_buttons.append(extra_frame)
    return AbstractBrowser().get_scan_browser_layout(section=section,extra_buttons=extra_buttons)+[[get_right_click_multi(key=text_to_key('file text',section=section),args={**expandable()})]]

