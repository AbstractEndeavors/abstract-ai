import os,threading
from abstract_gui import sg,AbstractBrowser,text_to_key,make_component,ensure_nested_list,expandable,RightClickManager,get_screen_dimensions,AbstractWindowManager
from io import BytesIO
from PIL import Image, ImageTk
from io import BytesIO
import requests
from PIL import Image
window_mgr = AbstractWindowManager()
tokenInfo_mgr=None

def return_range(i=None, k=None, divisor=None, divisorAfter=None):
    i = i or 0  # Default start is 0
    k = k or 100  # Default end is 100

    return [
        j for j in range(i, k)
        if (
            divisor is None  # No divisor, return all numbers
            or (divisorAfter is not None and j < divisorAfter)  # Before divisorAfter, all numbers included
            or (divisorAfter is None or j >= divisorAfter and j % divisor == 0)  # Apply divisor after divisorAfter
        )
    ]
from io import BytesIO

def get_image(image_url, new_size=(300, 300)):
    # Fetch the image content
    if image_url in [None, 0, '', ' ']:
        return None
    
    response = requests.get(image_url)
    if response.status_code == 200:
        # Use BytesIO to convert bytes data to a 'file-like object' that PIL can work with
        image_data = BytesIO(response.content)

        # Open the image with PIL (Pillow)
        image = Image.open(image_data)

        # Resize the image
        resized_image = image.resize(new_size)

        # Convert the resized image to a format that can be displayed
        bio = BytesIO()  # A new BytesIO object for the converted image
        resized_image.save(bio, format="PNG")  # Save the image as PNG to bio
        return bio.getvalue()
    else:
        return {}
def load_image(url=None,filePath=None, new_size=(300, 300)):
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            resized_image = image.resize(new_size)
            bio = BytesIO()
            resized_image.save(bio, format="PNG")
            Image.open(image_data)
            return bio.getvalue()
        else:
            return sg.Text("Failed to load the image.")
        import io

right_click_mgr=RightClickManager()
def get_standard_screen_dimensions(width=0.70,height=0.80):
    return get_screen_dimensions(width=width,height=height)
window_width,window_height=get_standard_screen_dimensions()
class WalletManager:
    def __init__(self):
        self.env_directories = []
        self.env_keys = []
        self.current_selection = {"path": os.getcwd(), "key": ""}
    
    def add_env_key(self, key):
        if key not in self.env_keys:
            self.env_keys.append(key)
        return self.env_keys
    
    def get_env_keys(self):
        return self.env_keys
    
    def delete_env_key(self, key):
        if key in self.env_keys:
            self.env_keys.remove(key)
        return self.env_keys
    
    def add_env_directory(self, directory):
        if directory not in self.env_directories:
            self.env_directories.append(directory)
        return self.env_directories
    
    def get_env_directories(self):
        return self.env_directories
    
    def delete_env_directory(self, directory):
        if directory in self.env_directories:
            self.env_directories.remove(directory)
        return self.env_directories
    
    def update_current_env(self, path=None, key=None):
        self.current_selection = {"path": path, "key": key}
        return self.current_selection
    
    def save_config(self, filename):
        with open(filename, 'w') as f:
            f.write(f"env_keys={self.env_keys}\n")
            f.write(f"env_directories={self.env_directories}\n")
    
    def load_config(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("env_keys="):
                    self.env_keys = line.split('=')[1].strip().split(',')
                elif line.startswith("env_directories="):
                    self.env_directories = line.split('=')[1].strip().split(',')
wallet_mgr = WalletManager()
def get_output_options()->list:
    return [
        [
         make_component("Button",button_text="SUBMIT QUERY",key="-SUBMIT_QUERY-", disabled=False,enable_evete=True),
         make_component("Button",button_text="CLEAR REQUESTS",key='-CLEAR_REQUESTS-', disabled=False,enable_evete=True),
         make_component("Button",button_text="CLEAR CHUNKS",key='-CLEAR_CHUNKS-', disabled=False,enable_evete=True),
         make_component("Button",button_text="GEN README",key='-GENERATE_README-', disabled=False,enable_evete=True)]
    ]
def generate_bool_text(title:str,args:dict={})->object:

        
    return make_component("Frame",title, layout=[[get_right_click_multi(key=text_to_key(text=title,section='text'),args=args)]],**expandable())
def get_tab_layout(title:str,layout:list=None)->object:
    if not layout:
        layout = get_right_click_multi(key=text_to_key(title),args={**expandable(size=(None, 5))})
    return make_component("Tab",title.upper(),ensure_nested_list(layout))

def make_default_checkbox(title:str,default:bool=True)->object:
    return make_component("Checkbox",title,key=text_to_key(text=title,section='bool'),enable_events=True,default=default)

def get_column(layout:list,args:dict={})->object:
    return make_component("Column",ensure_nested_list(layout),**args)

def get_tab_group(grouped_tabs:list,args:dict={})->object:
    return make_component("TabGroup",ensure_nested_list(grouped_tabs),**args)

def roles_js()->dict:
    return {'assistant':'you are an assistant','Elaborative': 'The model provides detailed answers, expanding on the context or background of the information. E.g., "What is the capital of France?" Answer', 'Socratic': 'The model guides the user to the answer through a series of questions, encouraging them to think critically.', 'Concise': 'The model provides the shortest possible answer to a question.', 'Friendly/Conversational': 'The model interacts in a more relaxed, friendly manner, possibly using casual language or even humor.', 'Professional/Formal': 'The model adopts a formal tone, suitable for professional settings.', 'Role-Playing': 'The model assumes a specific character or role based on user instructions. E.g., "You\'re a medieval historian. Tell me about castles."', 'Teaching': 'The model provides step-by-step explanations or breakdowns, as if teaching a concept to someone unfamiliar with it.', "Debative/Devil's Advocate": 'The model takes a contrarian view to encourage debate or show alternative perspectives.', 'Creative/Brainstorming': 'The model generates creative ideas or brainstorming suggestions for a given prompt.', 'Empathetic/Supportive': 'The model offers emotional support or empathy, being careful not to provide medical or psychological advice without proper disclaimers.'}

def roles_keys()->list:
    return list(roles_js().keys())

def content_type_list()->list:
    return ['application/json','text/plain', 'text/html', 'text/css', 'application/javascript',  'application/xml', 'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp', 'audio/mpeg', 'video/mp4', 'video/webm', 'audio/ogg', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/octet-stream', 'application/zip', 'multipart/form-data', 'application/x-www-form-urlencoded', 'font/woff', 'font/woff2', 'font/ttf', 'font/otf', 'application/wasm', 'application/manifest+json', 'application/push-options+json']
def env_section():
    return[[
        [make_component("Input", '', size=(15, 1), key="-ENV_KEY_INPUT-", events_enabled=True),
         make_component("Button", "Add Key", key="-ENV_KEY_ADD-", events_enabled=True, tooltip="Add new key")],
        
        [make_component('combo', value='', values=wallet_mgr.get_env_keys(), size=(13, 1), key="-ENV_KEY_SELECTION-",
                        events_enabled=True, tooltip="Select existing key"),
         make_component("Button", "Update Key", key="-ENV_KEY_UPDATE-", events_enabled=True, tooltip="Update the key value"),
         make_component("Button", "Delete Key", key="-ENV_KEY_DELETE-", events_enabled=True, tooltip="Delete the key")],
        
        [make_component('combo', value='', values=wallet_mgr.get_env_directories(), size=(30, 1), key="-ENV_PUBLIC_SELECTION-",
                        events_enabled=True, tooltip="Select public directories")],
        
        [make_component("FileBrowse", initial_directory=os.getcwd(), size=(15, 1), key="-ENV_DIRECTORY_BROWSER-",
                        events_enabled=True, tooltip="Browse directories"),
         make_component("Button", "Add Directory", key="-ENV_ADD_DIRECTORY-", events_enabled=True),
         make_component("Button", "Delete Directory", key="-ENV_DELETE_DIRECTORY-", events_enabled=True, tooltip="Delete the directory")],
        
        [make_component('combo', value='', values=[], size=(30, 1), key="-ENV_DIRECTORY_SELECTION-", events_enabled=True)]
    ],
    [
        make_component("Button", "UPDATE", key="-ENV_UPDATE-", events_enabled=True, tooltip="Save all changes"),
        make_component("Button", "SAVE CONFIG", key="-SAVE_CONFIG-", events_enabled=True, tooltip="Save environment settings to a file"),
        make_component("Button", "LOAD CONFIG", key="-LOAD_CONFIG-", events_enabled=True, tooltip="Load environment settings from a file")]
    ]
##create_prompt_tab
prompt_tab_keys=['request','prompt data','chunks','query','instructions']
def get_prompt_tabs(layout_specs={},args={}):
    layout = []
    for prompt_tab_key in prompt_tab_keys:
        layout.append(get_tab_layout(prompt_tab_key,layout=layout_specs.get(prompt_tab_key)))
    return get_tab_group(layout,args=args)
def get_right_click_multi(key:str,args:dict={})->object:
    return make_component("Multiline",**args,right_click_menu=right_click_mgr.get_right_click(key=key),key=key)
def get_left_right_nav(name,section=True,push=True):
    insert = f"{name} {'section ' if section else ''}"
    nav_bar = [make_component("Button",button_text="<-",key=text_to_key(f"{insert}back"),enable_events=True),
         make_component("input",default_text='0',key=text_to_key(f"{insert}number"),size=(4,1)),
         make_component("Button",button_text="->",key=text_to_key(f"{insert}forward"),enable_events=True)]
    if push:
        nav_bar=[make_component("Push")]+nav_bar+[make_component("Push")]
    return nav_bar
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

def get_progress_frame()->list:
    return [
        [
            make_component("Frame", 'PROGRESS', layout=[
                [
                    make_component("InputText", 'Awaiting Prompt', key='-PROGRESS_TEXT-', background_color="light blue", auto_size_text=True, size=(20, 20)),
                    make_component("ProgressBar", 100, orientation='h', size=(10, 20), key='-PROGRESS-'),
                    make_component("Input", default_text='0', key=text_to_key("query count"), size=(30, 20), disabled=True, enable_events=True)
                ]
            ]),
            make_component("Frame", 'query title', layout=[
                [
                    make_component("Input", default_text="title of prompt", size=(30, 1), key=text_to_key('title input'))
                ]
            ]),
            make_component('Frame', "response nav", [
                get_left_right_nav(name='response text',section=False,push=False)
            ])
        ]
    ]
def swap_commands():
    return sg.Frame('Swap Commands', layout=[
        [sg.Frame("Slippage", layout=[[sg.Combo(values=return_range(divisor=5, divisorAfter=10), size=(20, 1), key="-SLIPPAGE-")]])],
        [sg.Frame("Native", layout=[[sg.Input('', size=(20, 1), disabled=True, key="-NATIVE-")]])],
        [sg.Frame("Token", layout=[[sg.Input('', size=(20, 1), disabled=True, key="-TOKEN-")]])],
        [sg.Frame("Exchange", layout=[[sg.Combo(values=[], size=(20, 1), key="-EXCHANGE-")]])],
        [sg.Frame("Volume", layout=[[sg.Input('', size=(20, 1), disabled=True, key="-VOLUME-")]])],
        [sg.Frame("Market Cap", layout=[[sg.Input('', size=(20, 1), disabled=True, key="-MARKETCAP-")]]),
        [sg.Frame("Target Floor", layout=[[sg.Input('', size=(20, 1), key="-TARGETFLOOR-")]])],
        [sg.Frame("Target Ceiling", layout=[[sg.Input('', size=(20, 1), key="-TARGETCEILING-")]])],
        [sg.Frame("Target Profit", layout=[[sg.Combo(values=return_range(), size=(20, 1), key="-TARGETPROFIT-")]])],
        [sg.Button("BUY", key="-BUY-"), sg.Button("SELL", key="-SELL-"), sg.Button("AUTOTARGET", key="-AUTOTARGET-")]]
    ])
def currentTokenInfo():
    # Define column size
    
    # Left column with Mint, Description, Owner, MintAuthority, etc.
    
 
    layout=sg.Frame("Token URI", layout=[[sg.Image(data=load_image(url="https://solcatcher.io/static/solCatcher.png", new_size=(500, 400)), size=(500, 400), key="-IMAGE-")]])
    

    return layout
def abstract_browser_layouts(section=None,extra_component=None):
    
    inputs = make_component("Input",key=text_to_key("chunk title",section=section),size=(15,1))
    frames = make_component("Frame",'chunk title',layout=ensure_nested_list(inputs))
    chunk_title = make_component('Column',ensure_nested_list(frames))
    chunk_data_buttons = swap_commands()
    
    extra_buttons = [chunk_data_buttons,chunk_title]
    if extra_component != None:
        extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(extra_component))))
        extra_buttons.append(extra_frame)
def abstract_browser_layout(section=None,extra_component=None):
    inputs =  currentTokenInfo()
    frames = currentTokenInfo()
    chunk_title = currentTokenInfo()
    chunk_data_buttons = swap_commands()
    
    extra_buttons = [chunk_data_buttons,chunk_title]
    if extra_component != None:
        extra_frame = make_component('Column',ensure_nested_list(make_component("Frame",'output',layout=ensure_nested_list(extra_component))))
        extra_buttons.append(extra_frame)
    return AbstractBrowser().get_scan_browser_layout(section=section,extra_buttons=extra_buttons)+[[get_right_click_multi(key=text_to_key('file text',section=section),args={**expandable(size=(None, 5))})]]

def utilities()->list:
    layout = []
    collate_responses=make_component("Checkbox",'Collate Responses', key=text_to_key("COLLATE_BOOL",section='responses'), enable_events=True)
    json_to_string=make_component("Checkbox",'Json to String', key=text_to_key("FORMAT_JSON_TO_STRING",section='responses'), enable_events=True)
    key_selection=make_component("Frame",'response key',layout=ensure_nested_list(make_component("Combo",[], size=(15,1),key=text_to_key("response key selection",section='responses'), enable_events=True)))
    extra_component_responses = [make_component('Column',ensure_nested_list([[collate_responses],[json_to_string]])),make_component('Column',ensure_nested_list(key_selection))]
    format_json=make_component("Checkbox",'format json',default = True,key=text_to_key("format json to string",section='responses'), enable_events=True)
    layout.append(make_component("Tab",'SETTINGS', ensure_nested_list(make_component("Column", [],**expandable(scroll_vertical=True,scroll_horizontal=True))),**expandable(scroll_horizontal=True))),
    layout.append(make_component("Tab",'RESPONSES', abstract_browser_layout(section='responses',extra_component = extra_component_responses),key=text_to_key(text='response tab'),**expandable(size=(50, 100)))),
    layout.append(make_component("Tab",'Files', abstract_browser_layout(section='files'),**expandable(size=(800, 800)),key=text_to_key(text='file tab'))),
    layout.append(make_component("Tab",'urls', [],**expandable(size=(800, 800)),key=text_to_key(text='url tab'))),
    layout.append(make_component("Tab",'feedback', [],**expandable(size=(800, 800)),key=text_to_key(text='feedback tab')))
    return  make_component("TabGroup",ensure_nested_list(layout),**expandable(size=(None,int(window_height))))
def get_new_pairs(data={}):
    headers = {'Content-Type' :'application/json'}
    #response = requests.post('http://solcatcher.io/get_new_pairs', json=data, headers=headers)
    #return response.json()
def get_all_coin_vars():
    return [[[make_component("Frame","total",layout=[[make_component("Text","$"),
                                             make_component("Input",'',disabled=True,size=(15,1),key="-TOTAL_PRICE-")]]),
    make_component("Frame","symbol",layout=[[make_component("Input",'',disabled=True,size=(10,1),key="-SYMBOL-")]]),
    make_component("Frame","price",layout=[[make_component("Text","$"),
                                            make_component("Input",'',disabled=True,size=(10,1),key="-PRICE-")]]),
    make_component("Frame","price",layout=[[make_component("Text","$"),
                                            make_component("Input",'',disabled=True,size=(10,1),key="-DECIMALS-")]])]],
    [[make_component("Frame","token",layout=[[make_component("Input",'',disabled=True,size=(60,1),key="-TOKEN-")]])],
    [make_component("Frame","mint",layout=[[make_component("Input",'',disabled=True,size=(60,1),key="-MINT_DISPLAY-")]])],
    [make_component("Frame","address",layout=[[make_component("Input",'',disabled=True,size=(60,1),key="-ADDRESS_DISPLAY-")]])],
                    
        [sg.Frame("Metadata Address", layout=[[sg.Input('', disabled=True, expand_x=True, key="-METADATAADDRESS-")]])],
        [sg.Frame("Owner", layout=[[sg.Input('', disabled=True, expand_x=True, key="-OWNER-")]])],
        [sg.Frame("Mint Authority", layout=[[sg.Input('', disabled=True, expand_x=True, key="-MINTAUTHORITYADDRESS-")]])],
        [sg.Frame("Update Authority", layout=[[sg.Input('', disabled=True, expand_x=True, key="-UPDATEAUTHORITYADDRESS-")]])],
        [sg.Frame("Freeze Authority", layout=[[sg.Input('', disabled=True, expand_x=True, key="-FREEZEAUTHORITYADDRESS-")]])]
     ]]
def currentTokenInfo():
    # Define column size
    return [
        [make_component("Text","Log Messages", size=(40, 1),key="-MESSAGE_DISPLAY-"),[[sg.Frame("Description", layout=[[sg.Multiline('', expand_x=True, expand_y=True, key="-DESCRIPTION-", enable_events=False)]])],
            [sg.Frame("Token URI", layout=[[sg.Image(data=load_image(url="https://solcatcher.io/static/solCatcher.png", new_size=(500, 400)), size=(500, 400), key="-IMAGE-")]])]],
        [make_component("ListBox",[get_new_pairs(data={})],size=(45,10),key='-WALLET-',enable_events=True)],

        [make_component("multiline",key="-LOG-", size=(60, 15), autoscroll=True, disabled=True)],
        [make_component("Input",'',size=(70,1),key="-ADDRESS_INPUT-",events_enabled=True)],
        [make_component("Button","Find Pair",key="-START-",events_enabled=True),
         make_component("Button","Stop",key="-STOP-",events_enabled=True),
         make_component("Button","Exit",key="-EXIT-",events_enabled=True)],
        ]]




    return layout
def get_standard_screen_dimensions(width=0.70,height=0.80):
    return get_screen_dimensions(width=width,height=height)
def get_prompt_tabs(layout_specs={},args={})->list:
    layout = []
    
    for prompt_tab_key in prompt_tab_keys:
        layout.append(get_tab_layout(prompt_tab_key,layout=layout_specs.get(prompt_tab_key)))
    return get_tab_group(layout,args=args)   
def get_prompt_tabs(layout_specs={},args={})->list:
    layout = []
    
    for prompt_tab_key in prompt_tab_keys:
        layout.append(get_tab_layout(prompt_tab_key,layout=layout_specs.get(prompt_tab_key)))
    return get_tab_group(layout,args=args)  
def get_total_layout()->list:
    window_width,window_height=get_standard_screen_dimensions()
    
    return [make_component("TabGroup",ensure_nested_list([make_component("Tab",'urls', abstract_browser_layout(section=currentTokenInfo(),extra_component=env_section()),**expandable(size=(None,int(window_height))))]))]#,[[sg.Frame("Description", layout=[[sg.Multiline('', expand_x=True, expand_y=True, key="-DESCRIPTION-", enable_events=False)]])],**expandable(size=(800, 800)),key=text_to_key(text='url tab')]])]
 #                                                       make_component("Tab",'urls', get_all_coin_vars(),**expandable(size=(800, 800)),key=text_to_key(text='url tab')),
##                                                        make_component("Tab",'urls', env_section(),**expandable(size=(800, 800)),key=text_to_key(text='url tab')))]
                                                        
        
window_mgr = AbstractWindowManager()
window_name = window_mgr.add_window(window_name="Solana Token Monitor",title="Chat GPT Console",exit_events=['EXIT','ABORT'],layout=get_total_layout(),window_height=0.7,window_width=0.8,**expandable())

gui_thread = threading.Thread(target=window_mgr.while_window(), daemon=True)
gui_thread.start()
