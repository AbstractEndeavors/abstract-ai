from abstract_utilities import make_list,get_any_value,safe_read_from_json,write_to_file,safe_json_loads,eatAll
import os
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

def get_data_from_response_file(file_path):
    if file_path:
        if os.path.isfile(file_path):
            data = safe_read_from_json(file_path)
            prompt_content = get_prompt_content(data)
            prompt_pieces = split_prompt_data(prompt_content)
            response_content = get_response_content(data)
            return prompt_pieces,response_content
    return None,None

def clean_list(list_obj):
    while '' in list_obj:
        list_obj.remove('')
    return list_obj
def collate_responses(directory:(str),response_keys:(str or list)=[]):
    response_keys = make_list(response_keys) or ['api_response']
    file_list=[]
    if isinstance(directory,str):
        if os.path.isfile(directory):
            file_list=[directory]
        elif os.path.isdir(directory):
            directory_list = os.listdir(directory)
            for i,file in enumerate(directory_list):
                file_path=file
                if not os.path.isfile(file):
                    file_path = os.path.join(directory,file)
                if os.path.isfile(file_path):
                    file_list.append(new_file_path)
            file_list = get_list_of_file_type(file_list,'json')
    elif isinstance(directory,list):
        file_list=[]
        for path in directory:
            if os.path.isfile(path):
                file_list.append(path)
    description_data={}
    for file_path in file_list:
        baseName,ext=os.path.splitext(file_path)
        prompt_content,response_content = get_data_from_response_file(file_path)
        title = response_content.get('generate_title',baseName)
        if title not in list(description_data.keys()):
            description_data[title]= ['']
            
            for chunk in range(prompt_content.get('total_chunks',1)):
                description_data[title].append('')
        response_data_list=[]
        for response_key in response_keys:
            response_data = get_any_value(response_content,response_key)
            if response_data:
                response_data_list.append(response_data)
        response_num = prompt_content.get('chunk_num',0)
        description_data[title][response_num] = '\n'.join(clean_list(response_data_list))

    for key,values in description_data.items():
        description_data[key]='\n'.join(clean_list(values))
    return description_data
def get_api_response_value(response):
    response = make_list(get_any_value(response,'content') or None)[-1] or response
    response = safe_json_loads(response)
    if not isinstance(response,dict):
        generate_title = "generate_title"
        api_response = "api_response"
        result = response
        if generate_title in result:
            result = result.split(generate_title)[0]
            result = result.split(api_response)[-1]
            result = eatAll(result,[':',',','"',"'",' ','\n','\t'])
    else:
        result = response.get('api_response',response)
    return result
