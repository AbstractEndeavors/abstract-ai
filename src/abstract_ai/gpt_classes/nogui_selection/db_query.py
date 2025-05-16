from abstract_database import *
from conn_manager import *
from query_all import *
from abstract_ai import async_get_xlsx_file_path_from_response_vars
from abstract_security import *
from prompt_manager import *
from datetime import datetime

def get_db_query():
    file_path = get_last_created_response_file_path()
    return generate_query_from_recent_response(file_path)
def get_db_values(dbName,dbType):
    keys = {"user":None,"dbname":None,"host":None,"port":None,"password":None}
    for key,value in keys.items():
        env_key = get_db_key(dbName,dbType,key)
        keys[key]=get_env_key_value(env_key)
    return keys
def get_db_key(dbName,dbType,extra=None):
    key = f"{dbName.upper()}_{dbType.upper()}"
    if extra:
        key+=f"_{extra.upper()}"
    return key
def get_env_key_value(env_key):
    return get_env_value(env_key,deep_scan=True)
def search_env_path(dbName,dbType):
    return get_env_path(get_db_key(dbName=dbName,dbType=dbType),deep_scan=True)
def get_connection_manager(dbName,dbType):
    env_path = search_env_path(dbName=dbName,dbType=dbType)
    return connectionManager(dbName=dbName,dbType=dbType,env_path=env_path)
def get_db_mgr(dbName,dbType):
    env_path = search_env_path(dbName=dbName,dbType=dbType)
    conn_mgr = get_connection_manager(dbName=dbName,dbType=dbType)
    return DatabaseManager(dbName=dbName,dbType=dbType,env_path=env_path,conn_mgr=conn_mgr)
def get_db_query(prompt,dbName,dbType,tableName,prompt_data=[],instructions=[],instruction_bools={},model=None,env_key=None):
    db_mgr = get_db_mgr(dbName,dbType)
    data = db_mgr.get_instruction_from_tableName(tableName)
    prompt_data.append(f"this data is only an example of the database, it is not the data nore is it represetnative of anything more than context and type values:\n\n{data}")
    env_path = search_env_path(dbName,dbType)
    dt_object = datetime.utcfromtimestamp(time.time())
    # Format the datetime object to the desired format: 'YYYY-MM-DD HH:MM:SS'
    instructions.append({"query_input":extra_instructions,"example":{"query": "SELECT * FROM table WHERE condition"},"default":True})
    instruction_bools['database_query']=True
    setup_mgr = setup_module(prompt=prompt,
                       env_path=env_path,
                       prompt_percentage=50,
                       model=model,
                       additional_instructions=instructions,
                       instruction_bools=instruction_bools,
                       prompt_data=prompt_data)

    #database_query = setup_mgr.response.get('database_query')
    file_path = os.path.join("/home/joben/Videos/excels","output.xlsx")
    return  asyncio.run(async_get_xlsx_file_path_from_response_vars(data=setup_mgr.prompt_mgr.create_prompt(),file_path=file_path,db_mgr=db_mgr,env_path=env_path,dbType=dbType,dbName=dbName,conn_mgr=db_mgr.conn_mgr))
dt_object = datetime.utcfromtimestamp(time.time())
formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
#extra_instructions = '''the time is: '''+f"{formatted_time}\n"+'''Always include a 'query' key containing the SQL query as a string. Ensure that the 'query' key is always present in the database_query object, and the query is valid SQL.\n\n"'''
input(formatted_time)
dbName='catalyst'
dbType='database'
prompt='please query the database for all names with the letter k'
tableName = 'dncdata'
response = get_db_query(prompt,dbName,dbType,tableName)
input(response)
