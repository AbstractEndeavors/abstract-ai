from abstract_gui import expandable,make_component,ensure_nested_list 
from os.path import basename
import os
def clean_list(list_obj:list=[])->list:
    while '' in list_obj:
        list_obj.remove('')
    return list_obj
def construct_layout(files_list:list,window_size:(int,int))->list:
    result=''
    # The main layout construction code
    mass_files = [
        [make_component("Text","Select multiple files:")],
        [make_component("Input",key='-FILES_LIST-', enable_events=True), make_component("FilesBrowse",key='-BROWSE-')],
        [make_component("Listbox",values=clean_list(files_list), size=(40, 5), key='-FILES_LISTBOX-', enable_events=True)],
        [make_component("Button",'Clear Selection'), make_component("Button",'add')],[make_component("Button",'Submit'),make_component('Button','Review'), make_component("Button",'Exit')]
    ]
    layout = [mass_files]
    layout.append([make_component("Frame","module name", layout=[[make_component("Input",key="-MODULE_NAME-", size=(10, 1))]])])
    layout.append([make_component("Frame","setup document", layout=[[make_component("Input",key="-SETUP_PATH-", size=(30, 1)), make_component("FileBrowse")]])])
    column_layout = []
    # Add multiline input for each file in the list
    for file_path in files_list:
        column_layout.append([make_component("Frame",f"Description for {basename(file_path)}:",ensure_nested_list([make_component("Multiline",size=(60, 5), key=file_path)]))])
    layout.append(ensure_nested_list(make_component("Column",layout=ensure_nested_list(column_layout),**expandable(size=(int(window_size[0]),None),scroll_vertical=True))))
    return layout

def read_from_file(file_path:str)->str:
    with open(file_path, 'r') as f:
        return f.read()

def read_me_window(file_path_list:list=[])->(str,list):
    window_size = make_component("Window").get_screen_size()
    window_size= [int(window_size[0]*0.30),int(window_size[1]*0.8)]
    layout = construct_layout(file_path_list,window_size)
    window = make_component("Window",'Module Descriptions Input', layout,**expandable(size=window_size))
    files_list=[]
    result=''
    file_descriptions = {}

    while True:
        event, values = window.read()

        if event == None or event == 'Exit':
            files_list=[]
            result=''
            break
        elif event == '-BROWSE-' or event == 'add':
            new_files_list = values['-FILES_LIST-'].split(';')
            files_list=window['-FILES_LISTBOX-'].Values
            for file in new_files_list:
                if file not in files_list:
                    files_list.append(file)
            # Track previously entered descriptions
            for file_path in window['-FILES_LISTBOX-'].Values:
                if file_path in values:
                    file_descriptions[file_path] = values[file_path]
            
            for file_path in files_list:
                if file_path not in window['-FILES_LISTBOX-'].Values:
                    window['-FILES_LISTBOX-'].Update(values=window['-FILES_LISTBOX-'].Values + [file_path])

            # Update the layout with new file paths
            window.close()
            layout = construct_layout(files_list,window_size)
            window =  make_component("Window",'Module Descriptions Input', layout,finalize=True,**expandable(size=window_size))
            
            # Fill in previously entered descriptions
            for file_path, description in file_descriptions.items():
                if file_path in window.AllKeysDict:
                    if description:
                        window[file_path].Update(value=description)
            
        elif event  in ['Review','Submit']:
            files_list=window['-FILES_LISTBOX-'].Values
            result = generate_overview(values, window['-FILES_LISTBOX-'].Values)
            if event == 'Review':
                make_component("popup_scrolled",result, title="Modules Overview", size=(60, 30))
            elif event == 'Submit':
                break
        elif event == 'Clear Selection':
            window['-FILES_LISTBOX-'].update([])
    
    window.close()
    return result,files_list
def generate_overview(values:dict,files_list:list)->str:
    module_name = values["-MODULE_NAME-"]
    prompt_intro = f"""i have a module called {module_name}, id like to make a thurough readme for it

i am hoping that the intro and README.md directory can be established from this initial information that will be provided in the prompt data. 

so for this query, a strong introduction, a contents directory, install information, and any professional addages that are expected in a github/pypi readme. 

after this query i will send the scripts one by one such that the rest of the README.md can be written in sections\n\n
"""
    setup_doc = values['-SETUP_PATH-']
    setup_data=''
    if setup_doc:
        if os.path.isfile(setup_doc):
            setup_data = read_from_file(setup_doc)
        else:
            setup_data = setup_doc
        setup_data=f'here is the setup.py:\n{setup_data}\n\n'
    files = ''
    for file in files_list:
        files+=file+'\n'
    if files:
        files=f"the following paths are the various util files within the module:\n{files}\n\n"
    over_view_intro = f"Each module includes a suite of functions should be thoroughly documented within their docstrings, including purpose, input parameters, and return values.\n## Modules Overview\n\n"
    result = f"{prompt_intro}{files}{setup_data}{over_view_intro}"
    for file_path, description in values.items():
        if file_path in files_list:
            if not description:
                description = "[TODO: Add brief module overview here]"
            else:
                if isinstance(description,list):
                    description=description[0]
                description = description.strip()
            
            result += f"### {basename(file_path)}\n\n{description}\n\n"
    return result

