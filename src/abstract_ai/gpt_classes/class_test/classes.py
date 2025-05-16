tests='''#ResponseManagement
    def update_response_mgr(self)->None:
        self.response_mgr = ResponseManager(prompt_mgr=self.prompt_mgr,api_mgr=self.api_mgr)
        
    def get_new_api_call_name(self)->None:
        """
        A helper method that generates and appends a new unique API call name to the api_call_list.
 	"""
        call_name = create_new_name(name='api_call',names_list=self.api_call_list)
        if call_name not in self.api_call_list:
            self.api_call_list.append(call_name)

    def start_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()    
    def query_event_check(self) -> bool:
        if self.event == "-SUBMIT_QUERY-":
            if not self.submission_in_progress:
                self.submission_in_progress = True
                self.get_new_api_call_name()
                # Submit the coroutine to the event loop
                future = asyncio.run_coroutine_threadsafe(self.submit_query(), self.loop)
                # Optionally, handle the result or exceptions
                future.add_done_callback(self.handle_future_result)
            else:
                self.logger.info("Submission already in progress.")
            self.event = None
        else:
            return False
        return True

    def handle_future_result(self, future):
        try:
            result = future.result()
            # Process the result if needed
        except Exception as e:
            self.logger.error(f"Error in async task: {e}")
    def submit_event(self):
        self.get_new_api_call_name()
        self.start_query = False
        self.updated_progress = False
        self.response_mgr.re_initialize_query()
        asyncio.run(self.submit_query())
        self.submission_in_progress = False  # Reset the flag when done
    
    def get_dots(self)->None:
        """
        This is a helper method used in the update_progress_chunks method. It manages the progress tracking visual
        indication in the UI. It updates the dots string depending on the current state of the dots. If the dots string
        is full of dots, it resets it to empty.
        """
        count = 0
        stop = False
        dots = ''
        for each in self.dots: 
            if each == ' ' and stop == False:
                dots+='.'
                stop = True
            else:
                dots+=each
        self.dots = dots
        if stop == False:
            self.dots = '   '
        get_sleep(1)
        status='Testing'
        if self.test_bool == False:
            status = "Updating Content" if not self.updated_progress else "Sending"
        self.window_mgr.update_value(key='-PROGRESS_TEXT-', value=f'{status}{self.dots}')
        
    def update_progress_chunks(self,done:bool=False)->None:
        """
        updates the progress bar and text status in the GUI, depending on the amount of chunks processed. If the
        process is completed, it updates the UI with a sent status and enables the '-SUBMIT_QUERY-' button again.
        uses the helper get_dots method for dynamic visual indication of the processing.
	"""
        self.total_dists=0
        for dist in self.chunk_token_distributions:
            self.total_dists +=len(dist)
        i_query = int(self.response_mgr.i_query)
        if done == True:
            self.window['-PROGRESS-'].update_bar(100, 100)
            self.window_mgr.update_value(key='-QUERY_COUNT-', value=f"a total of {self.total_dists} chunks have been sent")
            self.window_mgr.update_value(key='-PROGRESS_TEXT-', value='SENT')
            self.updated_progress = True
        else:
            self.get_dots()
            self.window['-PROGRESS-'].update_bar(i_query, self.total_dists)
            if i_query == 0 and self.total_dists!= 0 :
                i_query = 1
            self.window_mgr.update_value(key='-QUERY_COUNT-', value=f"chunk {i_query} of {self.total_dists} being sent")
            
    # checks if the Response Manager has completed the query process.         
    def check_response_mgr_status(self)->bool:
        """
        checks if the Response Manager has completed the query process. It returns a Boolean indicating the status.
	"""
        if not self.test_bool:
            return self.response_mgr.query_done
        return self.start_query
    
    # Manages the process of submitting queries to the GPT AI
    async def submit_query(self) -> None:
        try:
            # Update the GUI components from the main thread using a thread-safe method
            self.window.write_event_value('-DISABLE_SUBMIT_BUTTON-', True)

            self.dots = '...'
            self.start_query = False
            if self.test_bool:
                self.latest_output = [safe_read_from_json(self.test_file_path)]
            else:
                self.latest_output = await self.get_query() or []
            self.output_list.append(self.latest_output)
            self.logger.error(f"recent output_list: {self.output_list}")
            self.update_progress_chunks(done=True)
            self.update_last_response_file()
            self.update_text_with_responses()
            # Re-enable the submit button
            self.window.write_event_value('-ENABLE_SUBMIT_BUTTON-', True)
            if not self.window_mgr.get_values()['-REUSE_CHUNK_DATA-']:
                self.update_prompt_data('')
            self.response = False
        finally:
            self.submission_in_progress = False
        
        
    async def get_query(self) -> None:
        self.response = await self.response_mgr.initial_query()
        return self.response
    def response_event_check(self)->bool:
        """
        Checks if a response event has been triggered.

        A response event is triggered when a user interacts with the response management interface.

        Returns:
            bool: True if a response event has been triggered, otherwise False
        """
        if self.event == "-COLLATE_RESPONSES_BOOL-":
            if self.window_mgr.get_values()["-COLLATE_RESPONSES_BOOL-"]:
                files_list = self.window['-FILES_LIST_RESPONSES-'].Values
                if len(files_list)>0:
                    collator = FileCollator(files_list)
                    collated_responses=collator.get_gollated_responses(files_list,key_value = 'response')
                    self.window_mgr.update_value('-FILE_TEXT_RESPONSES-',collated_responses)
                    
        elif self.event in ['-RESPONSE_TEXT_BACK-','-RESPONSE_TEXT_FORWARD-']:
            self.determine_output_display(self.event)
            
        elif self.event == 'Copy Response':
            active_tab_key = self.window_mgr.get_values()['-TABS-']  # get active tab key
            # Construct the key for multiline text box
            multiline_key = active_tab_key.replace('TAB','TEXT')
            if multiline_key in self.window_mgr.get_values():
                text_to_copy = self.window_mgr.get_values()['-FILE_TEXT-']
                pyperclip.copy(text_to_copy)
        else:
            return False
        return True
    
    def get_output_response(self,model:str="None",title:str="None",request:str="None",response:str="None",output_files:str="None")->str:
        """
        A helper method that formats the output string of a response in a clear and readable manner.
        It includes information about the model, title, user request, and AI response.
 	"""
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
        output_keys = []
        self.last_prompt= get_any_value(safe_json_loads(self.current_output),'prompt')
        self.last_response = get_response(self.current_output)
        self.last_file_path= get_any_data(self.current_output,'file_path')
        self.last_title= get_title(self.current_output)
        self.unlist_self(["last_prompt","last_title","last_file_path","last_prompt"])
        self.last_content = get_any_data(self.last_response,'content')
        self.last_api_response = get_api_response(self.last_response)
        self.last_model =get_any_value(safe_json_loads(self.last_response),'model')
        self.unlist_self(["last_model","last_api_response","last_content"])
        self.window_mgr.update_value(key=text_to_key('title input'),value=self.last_title)
        self.database_output_file = generate_query_from_recent_response(file_path=self.last_file_path)
        response_content = self.last_content
        if self.last_api_response:
            response_content=self.last_api_response
            self.delegate_instruction_text()
        self.window_mgr.update_value('-RESPONSE-',self.get_output_response(model=self.last_model,
                                                                           title=self.last_title,
                                                                           request=self.request_data_list[self.get_current_request_data()],
                                                                           response=response_content,output_files=self.database_output_file))
        
    def get_current_request_data(self)->int:
        num=0
        for i,data in enumerate(self.prompt_data_list):
            num+=len(data)
            if self.response_text_number_actual<=num:
                if i>len(self.request_data_list):
                    return len(request_data_list)-1
                return i
        return len(self.request_data_list)-1
    def unlist_self(self,keys:list):
        """
        A helper method that takes a list of keys as a parameter, iterates over each key, and checks if
        the value of the corresponding key in the class is a non-empty list. If it is, it updates the class's attribute with the last element in the list.
 	"""
        for key in keys:
            value = getattr(self,key)
            if isinstance(value,list) and value:
                value = value[-1]
            setattr(self,key,value)
    def initialize_output_display(self)->None:
        """
        Initializes the display of the latest output in the GUI.
        """
        if len(self.latest_output)>0:
            self.current_output=self.latest_output[-1]
        else:
            self.current_output=[]
        self.response_text_number_actual=0
        self.response_text_number_display=1
        self.window_mgr.update_value(key='-RESPONSE_TEXT_NUMBER-',value=self.response_text_number_display)
        self.update_output(output_iteration=0)
        
    def get_output_display_numbers(self)->None:
        """
        Retrieves the actual and display numbers of the current output for navigation purposes.
        """
        self.response_text_number_display = int(self.window_mgr.get_from_value('-RESPONSE_TEXT_NUMBER-'))
        self.response_text_number_actual = self.response_text_number_display-1
        
    def determine_output_display(self,event):
        """
        Determines the output to display based on the navigation event.

        Args:
            event: The navigation event that occurred
        """
        self.get_output_display_numbers()
        if self.event == '-RESPONSE_TEXT_BACK-':
            if self.response_text_number_actual >0:
                self.adjust_output_display(-1)
        elif self.event == '-RESPONSE_TEXT_FORWARD-':
            if self.response_text_number_display < len(self.latest_output):
                self.adjust_output_display(1)
                
    def update_output(self,output_iteration:int):
        """
        Updates the displayed output based on the given iteration.

        Args:
            output_iteration (int): The index of the output to display.
        """
        if output_iteration < len(self.latest_output) and output_iteration >=0:
            self.current_output = self.latest_output[output_iteration]
            self.update_text_with_responses()
            
    def adjust_output_display(self,num:int):
        self.response_text_number_actual+=num
        self.response_text_number_display+=num
        self.update_output(output_iteration=self.response_text_number_actual)
        self.window_mgr.update_value(key='-RESPONSE_TEXT_NUMBER-',value=self.response_text_number_display)
        
    def listbox_event_check(self)->bool:
        """
        Checks if a listbox event has been triggered and updates the GUI accordingly.

        Returns:
            bool: True if a listbox event has been triggered, otherwise False
        """
        event_triggered = False
        values = self.window_mgr.get_values()
        file_path = None

        if self.script_event_js['found'] == '-FILES_LIST-':
            selected_files = values[self.event]
            if selected_files:
                file_path = selected_files[0]
                event_triggered = True
        elif self.script_event_js['found'] == '-BROWSER_LIST-':
            directory = values[self.script_event_js['-DIR-']]
            selected_files = values[self.script_event_js['-BROWSER_LIST-']]
            if selected_files:
                file_path = os.path.join(directory, selected_files[0])
                event_triggered = True
        if self.window_mgr.get_from_value(text_to_key('database query bool', section='database')):
                contents = get_instruction_from_tableName(self.window_mgr.get_from_value(text_to_key('table configuration', section='database')))
                self.window_mgr.update_value(key=text_to_key('-FILE_TEXT-', section='database'), value=contents)
                self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-', section='database'), value=self.chunk_title)
        if file_path:
            if os.path.isfile(file_path):
                try:
                    contents = self.read_file_contents(file_path)  # Assuming read_file_contents is defined to handle different file types
                    contents = safe_json_loads(contents)
                    
                    if isinstance(contents,dict) and self.window_mgr.get_from_value(text_to_key('format json to string', section='responses')):
                        contents = format_json_key_values(contents)
                    self.window_mgr.update_value(key=self.script_event_js['-FILE_TEXT-'], value=contents)
                    self.chunk_title = os.path.basename(file_path)
                    self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-', section='files'), value=self.chunk_title)
                except Exception as e:
                    print(f"Cannot read from path {file_path}. Error: {e}")
            else:
                file_path = self.window_mgr.get_values()[self.script_event_js['-DIR-']]
                files_list = self.window_mgr.get_values()[self.script_event_js['-BROWSER_LIST-']]
                if file_path:
                    file_path = os.path.join(file_path,files_list[0])
                    if not os.path.isfile(file_path):
                        self.browser_mgr.handle_event(self.event,self.window_mgr.get_values(),self.window)
        return event_triggered

    get_instruction_from_tableName()
    def update_last_response_file(self)->None:
        """
        Updates the path to the last file that recorded a response.

        This function also updates the GUI with the contents of the new file.
        """
        if self.test_bool:
            self.last_response_file=self.test_file_path
        else:
            self.last_response_file = self.response_mgr.save_manager.file_path
        self.last_directory=os.path.dirname(self.last_response_file)
        self.window_mgr.update_value(key='-DIR_RESPONSES-',value=self.last_directory)
        self.update_response_list_box()
        self.window["-DIRECTORY_BROWSER_RESPONSES-"].InitialFolder=self.last_directory
        self.window["-FILE_BROWSER_RESPONSES-"].InitialFolder=self.last_directory
        self.initialize_output_display()
        
    def update_response_list_box(self)->None:
        """
        Update the List Box component that displays saved responses.

        This function is often called after a new API response has been received and saved.
        """
        if self.latest_output:
            for data in self.latest_output:
                file_path = get_any_value(data,'file_path')
                if file_path in self.new_response_path_list:
                    self.new_response_path_list.remove(file_path)
                self.new_response_path_list.append(file_path)
            files_list = self.window['-FILES_LIST_RESPONSES-'].Values
            if file_path in self.new_response_path_list:
                if file_path in files_list:
                    files_list.remove(file_path)
            files_list=self.new_response_path_list+files_list
            self.window_mgr.update_value('-FILES_LIST_RESPONSES-',args={"values":files_list})

    def aggregate_conversations(self,directory:str=None)->list:
        """
        Aggregates conversations from JSON files in the specified directory.

        Args:
            directory (str): The directory containing the JSON files. If none, it will take the current working directory.

        Returns:
            list: A list of aggregated conversations.
        """
        if directory == None:
            directory = os.getcwd()
        json_files, lsAll = [], []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    file = os.path.join(root, file)
                    json_files.append((get_file_create_time(file), file))
        sorted_json_files = sorted(json_files, key=lambda x: x[0])
        aggregated_conversations = []
        chat_log_file = open("chat_log.txt", "w")
        model = 'gpt'
        for file in sorted_json_files:
            file = file[1]
            data = safe_read_from_json(file)
            if data:
                relevant_values={}
                relevant_keys = ['id', 'object', 'created', 'model']
                for key in relevant_keys:
                    value = get_any_value(data,key)
                    if value:
                        relevant_values[key]=value
                if len(relevant_values.keys())==len(relevant_keys):
                    if file not in aggregated_conversations:
                        aggregated_conversations.append(file)
                    dir_name=os.path.dirname(file)
                    if dir_name not in self.response_directories_list:
                        self.response_directories_list.append(dir_name)
           
        #self.next_read_mgr.add_to_queue(self.window_mgr.update_value,'-FILES_LIST_RESPONSES-',args={"values":aggregated_conversations})
        return aggregated_conversations'''
manager_name = 'GptManager'
for test in tests.split('def ')[1:]:
        function_name = test.split('(')[0]
        print(f"self.{function_name}={function_name}")
        
