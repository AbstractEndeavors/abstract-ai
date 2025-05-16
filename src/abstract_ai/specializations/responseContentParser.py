from abstract_utilities import make_list,get_any_value,safe_read_from_json,write_to_file,safe_json_loads,eatAll
import os,glob
def get_raw_response_directory():
    return os.path.join(os.getcwd(),"response_data")
def get_latest_file(directory):
    # Initialize a variable to hold the latest file and the most recent creation time
    latest_file = None
    latest_time = None
    
    # Recursively search through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        # Skip directories that contain "raw_response" in their name
        dirs[:] = [d for d in dirs if "raw_response" not in d]
        files = [file for file in files if os.path.splitext(file)[-1] == '.json']
        for file in files:
            
            file_path = os.path.join(root, file)
            
            # Get the file's creation time
            file_time = os.path.getctime(file_path)
            
            # Compare and update the latest file if it's more recent
            if latest_time is None or file_time > latest_time:
                latest_time = file_time
                latest_file = file_path

    return latest_file

def get_last_created_response_file_path():
    raw_response_directory = get_raw_response_directory()
    
    # Return the latest file path or handle if no file exists
    latest_file = get_latest_file(raw_response_directory)
    
    if latest_file:
        return latest_file
    else:
        return "No files found in the directory."
def read_previous_query():
    recent_file_path = get_last_created_response_file_path()
    return safe_read_from_json(recent_file_path)
def parse_previous_query():
    response_mgr = ResponseFileCollator()
    return self.ordered_data[0]

def get_latest_responses():
    directories = {}
    for root, _, files in os.walk(get_raw_response_directory()):
        for file in files:
            if root not in directories:
                directories[root] = None
            file_path = os.path.join(root, file)
            file_time = os.path.getmtime(file_path)
            if directories[root] == None or directories[root][-1]< file_time:
                directories[root]=[file_path,file_time]
    return directories
def get_latest_response():
    latest = [get_last_created_response_file_path(),0]
    for key,value in get_latest_responses().items():
        if latest[-1] == 0 or value[-1] < latest[-1]:
            latest = value
    return latest[0]
def get_prompt_content(data):
    prompt_data = get_any_value(data,'prompt')
    message_data = get_any_value(prompt_data,'messages')
    if isinstance(message_data,list) and message_data:
        message_data = safe_json_loads(message_data[0])
    return get_any_value(message_data,'content')

def split_prompt_data(prompt_data):
    prompt_parts={}
    prompt_datas = prompt_data.split('-----------------------------------------------------------------------------')
    for prompt_data in prompt_datas[1:]:
        prompt_data = eatAll(prompt_data,['\n','',' ','\t'])
        if prompt_data[0] == '#':
            name = prompt_data[1:].split('#')[0]
            prompt_parts[name]=prompt_data[len(name)+2:]
    
    if 'chunk_data' in prompt_parts:
        chunk_data = eatAll(prompt_parts['chunk_data'],['\n','',' ','\t'])
        if 'this is chunk ' ==chunk_data[:len('this is chunk ')]:
            chunk_num,total_chunks = chunk_data[len('this is chunk '):].split('\n')[0].split(' of ')
            prompt_parts['chunk_num']=int(chunk_num)
            prompt_parts['total_chunks']=int(total_chunks)
    if prompt_parts:
        return prompt_parts
    return {"prompt":prompt_data}
def get_response_content(data):
    response_data = get_any_value(data,'response')
    choice_data = get_any_value(response_data,'choices')
    if isinstance(choice_data,list) and choice_data:
        choice_data = safe_json_loads(choice_data[0])
    return get_any_value(choice_data,'content')

def get_list_of_file_type(list_obj,ext_type):
    return_list=[]
    for file in list_obj:
        baseName,ext=os.path.splitext(file)
        if eatAll(ext,'.') == eatAll(ext_type,'.'):
            return_list.append(file)
    return return_list

def get_data_from_response(data=None,file_path=None):
    data = make_list(get_data(data=data,file_path=file_path) or None)[0]
    prompt_content = get_prompt_content(data)
    prompt_pieces = split_prompt_data(prompt_content)
    response_content = get_updated_response_content(data)
    return prompt_pieces,response_content

def clean_list(list_obj):
    while '' in list_obj:
        list_obj.remove('')
    return list_obj

import json
def get_data(data=None,file_path=None):
    data = data or file_path
    if data and isinstance(data,str) and os.path.isfile(data):
        data = safe_read_from_json(data)
    return safe_json_loads(data)
def get_any_data(data=None,key_value=None,file_path=None):
    data = make_list(get_data(data=data,file_path=file_path) or None)[0]
    if key_value == None:
        return data
    return  make_list(get_any_value(data, key_value) or None)[0]
def get_chunk_data(data=None,file_path=None):
    data = get_current_prompt_content(data=data,file_path=file_path)
    return {"chunk_num":get_any_value(data,"chunk_num"),"total_chunks":get_any_value(data,"total_chunks")}
def get_title(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return  make_list(get_any_value(data, 'generate_title') or None)[0]
def get_model(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    data = safe_json_loads(data)
    model=''
    if isinstance(data,dict):
        model = data.get('model')
        if model == None:
          model = make_list(get_any_value(data, 'model') or None)[0]
        return model
    return make_list(get_any_value(data, 'model') or None)[0]
def get_created(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return make_list(get_any_value(data, 'created') or None)[0]
def get_response(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return make_list(get_any_value(data,'response') or data)[0]
def get_choices(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return make_list(get_any_value(data,'choices') or None)[0]
def get_content(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return make_list(get_any_value(data,'content') or None)[0]
def get_file_path(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    return make_list(get_any_value(data,'file_path') or None)[0]
def get_response_content(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    response = get_response(data=data,file_path=file_path)
    if not response:
        response = get_any_value(safe_json_loads(data),'response')
    return response
def get_api_response(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    data = get_response_content(data=data,file_path=file_path)
    response_data = make_list(get_any_value(data,'api_response') or None)[0]
    if data and response_data == None and "'api_response':" in data or '"api_response":' in data:
        response_data = data.split("'api_response':")[-1].split('"api_response":')[-1]
        for key in ['notation','additional_responses','suggestions','generate_title','prompt_as_previous']:
            response_data= response_data.split(f"'{key}':")[0].split(f'"{key}":')[0]
    return response_data
def get_updated_response_content(data=None,file_path=None):
    response_content = get_response_content(data=data,file_path=file_path)
    content = get_content(response_content) or {}
    new_js = {
        "generate_title":get_title(data=data,file_path=file_path),
        "created":get_created(data=data,file_path=file_path),
        "model":get_model(data=data,file_path=file_path),
        "file_path":get_file_path(data=data,file_path=file_path)}
    if isinstance(content,dict):
        content.update(new_js)
    return content
def get_files_list(directory=None,files_list=None):
    files_list = files_list or directory
    if files_list and isinstance(files_list,str) and os.path.isdir(files_list):
        files_list = os.listdir(files_list)
    return files_list
def get_file_paths(directory=None,files_list=None):
    files_list = [os.path.join(directory or '',file) for file in get_files_list(directory=directory,files_list=files_list)]
    return files_list
def get_cronological_file_list(directory=None,files_list=None):
    files_list = get_files_list(directory=directory,files_list=files_list)
    content_data_list = sorted(
    files_list,
    key=lambda x: get_created(file_path=x)
    )
    prev_created=0
    for file_path in content_data_list:
        curr_created = int(get_created(file_path=file_path))
        if curr_created<prev_created:

            prev_created = curr_created
    return content_data_list
def get_ordered_data(directory=None,files_list=None):
    chron_files_list = get_cronological_file_list(directory=directory,files_list=files_list)
    return [get_data(file_path=file_path) for file_path in chron_files_list]
def get_ordered_response_data(directory=None,files_list=None):
    chron_files_list = get_cronological_file_list(directory=directory,files_list=files_list)
    return [get_updated_response_content(file_path=file_path) for file_path in chron_files_list]
def get_current_prompt_content(data=None,file_path=None):
    data = get_data(data=data,file_path=file_path)
    prompt_content = get_prompt_content(data)
    return split_prompt_data(prompt_content)
def get_ordered_chunk_sections(directory=None,files_list=None):
    ordered_data = get_ordered_data(directory=directory,files_list=files_list)
    return get_ordered_chunk_sections(ordered_data=ordered_data)
def get_chunk_sections(ordered_data):
    sections=None
    total_len = len(ordered_data)
    for i,data in enumerate(ordered_data):
        if sections == None or  make_list(get_chunk_data(data=data).get("chunk_num") or None)[-1] == 1:
            if sections == None:
                sections=[[i,total_len-1]]
            else:
                sections[-1][1]=i-1
            sections.append([i,total_len-1])
    return sections
def get_ordered_chunk_sections_data(directory=None,files_list=None):
    ordered_data = get_ordered_data(directory=directory,files_list=files_list)
    return get_chuk_sections_data(ordered_data)
def get_chuk_sections_data(ordered_data):
    output_chunk_sections = []
    chunkSection = []
    chunk_sections = get_chunk_sections(ordered_data)
    for j,ranges in enumerate(chunk_sections):
        for i in range(*ranges):
            chunkSection.append(ordered_data[i])
        output_chunk_sections.append(chunkSection)
        chunkSection = []
    return output_chunk_sections
def get_largest_chunk(directory=None,files_list=None):
    highest= [None,0]
    chunk_sections = get_ordered_chunk_sections_data(directory=directory,files_list=files_list)
    for i,chunk in enumerate(chunk_sections):
        if len(chunk)>highest[-1]:
            highest=[i,len(chunk)]
    return highest
class ResponseFileCollator:
    def __init__(self, directory=None,files_list=None, keyValue=None):
        self.files_list = get_file_paths(directory=directory)
        self.chronological_file_list = get_cronological_file_list(files_list=self.files_list)
        self.ordered_data = [get_data(file_path=file_path) for file_path in self.chronological_file_list]
        self.chunk_sections = get_ordered_chunk_sections_data(files_list=self.files_list)
        self.largest_chunk_section = get_largest_chunk(files_list=self.files_list)[0]
    def get_spec_data(self,keyValue = None,chunk_section=None,prompt_data = False,response_data = False,api_response = False,collated = False):
        data = self.ordered_data
        if chunk_section:
            if chunk_section == True:
                chunk_section = self.largest_chunk_section
            data = self.chunk_sections[chunk_section]
        if keyValue:
            data = [get_any_data(data=data,keyValue=keyValue) for data in data]
        if prompt_data:
            data = [get_current_prompt_content(data=data) for data in data]
        else:
            if response_data:
                data = [get_updated_response_content(data=data) for data in data]
            if api_response:
                data = [get_api_response(data=data)or data for data in data]
        
        if collated:
            data = '\n'.join([str(string) for string in data if string])
    
        return data

