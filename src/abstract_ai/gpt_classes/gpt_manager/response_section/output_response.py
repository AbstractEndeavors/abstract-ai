from ..dependencies import *
def get_output_response(self,model:str="None",title:str="None",request:str="None",response:str="None",output_files:str="None")->str:
    """
    A helper method that formats the output string of a response in a clear and readable manner.
    It includes information about the model, title, user request, and AI response.
    """
    self.logger.info(f"get_output_response..")
    model = f"#MODEL#{self.get_new_line(1)}{self.last_model}{self.get_new_line(2)}"
    title = f"#TITLE#{self.get_new_line(1)}{str(title)}{self.get_new_line(2)}"
    request = f"#USER REQUEST#{self.get_new_line(1)}{str(request)}{self.get_new_line(2)}"
    response = f"#RESPONSE#{self.get_new_line(2)}{str(response)}{self.get_new_line(2)}"
    output_files = f"#OUTPUT FILES#{self.get_new_line(1)}{str(output_files)}{self.get_new_line(2)}"
    return f"{model}{title}{request}{response}{output_files}"

def update_text_with_responses(self)->None:
    """
    gets the latest response from the AI, formats it using the get_output_response helper method,
    and updates the GUI's '-RESPONSE-' key with the formatted string.
    """
    self.logger.info(f"update_text_with_responses..")
    output_keys = []
    self.last_prompt_content,response_content = get_data_from_response(self.current_output)
    self.last_response_content = response_content
    self.last_request= self.last_prompt_content.get('prompt')
    self.last_file_path= get_file_path(self.last_response_content)
    self.last_title= get_title(self.last_response_content)
    self.last_model = get_model(self.last_response_content)
    self.last_api_response = self.last_response_content.get('api_response')
    self.window_mgr.update_value(key=text_to_key('title input'),value=self.last_title)
    #self.database_output_file = generate_query_from_recent_response(file_path=self.last_file_path)
    if self.last_api_response:
        response_content=self.last_api_response
        self.delegate_instruction_text()
    self.window_mgr.update_value('-RESPONSE-',self.get_output_response(model=self.last_model,
                                                                       title=self.last_title,
                                                                       request=self.last_request,
                                                                       response=response_content,
                                                                       output_files=self.last_file_path))
