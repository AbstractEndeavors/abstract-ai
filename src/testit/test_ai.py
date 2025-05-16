from abstract_utilities import *
def get_whole_brackets(obj,start=None):
    chars=''
    start = start or 0
    brackets_js = {'(':start,')':0}
    for char in str(obj):
        for key,value in brackets_js.items():
            if char and not char.replace(key,''):
                brackets_js[key]+=1
                vals = list(brackets_js.values())
                if vals[0] == vals[1]:
                    chars+=char
                    return chars
                break
        chars+=char
    return chars     
files = """/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:    response = input(f"{text} {choices}:({default}) ") or default
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:    return input(f"Enter {typ} value {action} in {parentObject}: ")
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:                input(rows)
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:            value = input(f"Enter value to filter by {column_name} (or press Enter to skip): ")
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:            choice = input("Enter your choice: ")
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:                file_path = input("Enter the file path to save the Excel file (default: output.xlsx): ") or "output.xlsx"
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:                error_message = input("Enter the error message to search for (e.g., 'Method not found'): ")
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/abstract_database_cmd.py:                confirm = input(f"Are you sure you want to delete the entire table '{table_name}'? (y/n): ").lower()
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/nogui_selection/db_query.py:    input()
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/file_section/responseContentParser.py:        input(description_data[title])
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/file_section/JsonHandler.py:    input(s)
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/gpt_classes/file_section/JsonHandler.py:        input(output_string)
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/specializations/responseContentParser.py:            input('out of o order')
/home/computron/Documents/pythonTools/modules/abstract_ai/src/abstract_ai/specializations/JsonHandler.py:    input(s)""".split('/home/')
for each in [each for each in files if each]:
    file_spl = each.split('.py:')
    file_path = f"/home/{file_spl[0]}.py"
    data = read_from_file(file_path)
    input_data = file_spl[-1]
    clean_input_data = eatAll(input_data,[' ','\t','\n'])
    if input_data in data:
        for chunk in data.split(input_data)[1:]:
            if chunk in data and 'input(f"Enter ' not in input_data and 'input("Enter ' not in input_data:
                input_data = f"{input_data}{chunk}"
                
                whole_bracket = get_whole_brackets(input_data)
                response = input(f"delete {whole_bracket}")
                if response == 'y':
                    data = data.replace(whole_bracket,'')
                    write_to_file(contents=data,file_path=file_path)
                    data = read_from_file(file_path)
