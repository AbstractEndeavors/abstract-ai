from abstract_gui import text_to_key
class AbstractNavigationManager:  # Replace with your actual class name
    def __init__(self,selfs,window_mgr)->None:
        self.window_mgr = window_mgr
        self.selfs =selfs
        self.action_keys = ['prompt_data','request','query','chunk','instructions']
    def chunk_event_check(self)->None:
        """
        Checks if any events related to the chunk UI elements were triggered and performs the necessary actions.
        """
        self.event,self.values,self.window=args
        # Simplified method to determine the type and direction of navigation
        navigation_type, navigation_direction = self.parse_navigation_event(self.event)

        # Early exit if the event is not a navigation event
        if not navigation_type:
            return

        # Retrieve navigation data based on the event
        nav_data = self.get_navigation_data(navigation_type)

        # Update the section and subsection numbers based on navigation
        self.update_navigation_counters(nav_data, navigation_direction)

        # Update the display based on the updated navigation data
        self.update_display(nav_data)

    def parse_navigation_event(self, event:str)->((None,None) or (str,str)):
        """
        Parses the event to extract navigation type and direction.
        """
        if event.startswith('-') and event.endswith('-'):
            parts = event[1:-1].lower().split('_')
            if 'back' in parts or 'forward' in parts:
                nav_type = '_'.join(parts[:-2]) if 'section' in parts else parts[0]
                nav_direction = parts[-1]
                return nav_type, nav_direction
        return None, None

    def get_navigation_data(self, navigation_type:str)->dict:
        """
        Retrieves the necessary data for navigation based on the navigation type.
        """
        nav_data = {
            'data_type': navigation_type,
            'section_number': int(self.window_mgr.get_from_value(f"-{navigation_type.upper()}_SECTION_NUMBER-")),
            'number': self.get_sub_section_number(navigation_type),
            'reference_object': self.get_reference_object(navigation_type)
        }
        return nav_data

    def get_sub_section_number(self, navigation_type:str)->int:
        """
        Retrieves the current sub-section number based on navigation type.
        """
        spl = self.window_mgr.get_event().split('_')
        section = spl[1]
        self.number_key = f"-{navigation_type.upper()}{'_SECTION' if len(spl)>= 3 else ''}_NUMBER-"
        return int(self.window_mgr.get_from_value(self.number_key)) if self.window_mgr.exists(self.number_key) else None

    def get_reference_object(self, navigation_type:str)->list:
        """
        Retrieves the reference object based on navigation type.
        """
        reference_js = {
            "request": self.selfs.request_data_list,
            "prompt_data": self.selfs.prompt_data_list,
            "chunk": self.selfs.prompt_mgr.chunk_token_distributions,
            "query": self.selfs.prompt_mgr.chunk_token_distributions,
            "instructions":self.selfs.prompt_data_list
            
        }
        return reference_js.get(navigation_type, [])

    def update_navigation_counters(self, nav_data:dict, direction:str)->None:
        """
        Updates section and subsection numbers based on the navigation direction.
        """
        def get_adjusted_number(current_number:int, reference_obj:list)->int:
            return max(0, min(current_number, max(0, len(reference_obj))))
        reference_obj = nav_data['reference_object']
        current_section_number = self.selfs.display_number_tracker[nav_data['data_type']]
        current_section_number = get_adjusted_number(current_section_number, reference_obj)
        if 'SECTION' in self.number_key:
            max_value = max(0, len(reference_obj) - 1)
            increment = 1 if direction == 'forward' else -1
            nav_data['section_number'] = max(0, min(current_section_number + increment, max_value))
            nav_data["number"]=0
        elif nav_data['data_type'] in ["chunk", "query"]:
            reference_obj = reference_obj[current_section_number]
            current_chunk_number = self.selfs.display_number_tracker['chunk_number']
            current_chunk_number = get_adjusted_number(current_chunk_number, reference_obj)

            max_value = max(0, len(reference_obj) - 1)
            increment = 1 if direction == 'forward' else -1
            nav_data['number'] = max(0, min(current_chunk_number + increment, max_value))

        self.update_display(nav_data)

    
    def update_number_tracker(self,nav_data:dict)->None:
        for key in self.action_keys:
            self.selfs.display_number_tracker[key]=nav_data["section_number"]
        self.selfs.display_number_tracker['chunk_number']=nav_data["number"]
        
    def update_data_displays(self,nav_data:dict)->None:
        self.selfs.update_request_data_display(nav_data["section_number"])
        self.selfs.update_prompt_data_display(nav_data["section_number"])
        action_keys = ['chunk','query']
        number_types = ['section_number','number']
        for action_key in self.action_keys:
            for number_type in number_types:
                self.window_mgr.update_value(text_to_key(f'{action_key}_{number_type}'),nav_data[number_type])
    def update_display(self, nav_data:dict)->None:
        """
        Updates the display based on the navigation data.
        """
        self.update_number_tracker(nav_data)
        self.update_data_displays(nav_data)
        #self.window_mgr.update_value("-CHUNK_SECTIONED_DATA-",self.selfs.prompt_mgr.chunk_token_distributions[nav_data["section_number"]][0]['chunk']['data'])
        chunk_section = max(0, min(nav_data['section_number'], len(self.selfs.prompt_mgr.chunk_token_distributions)-1))
        self.window_mgr.update_value(key='-QUERY-',value=self.selfs.prompt_mgr.create_prompt(chunk_token_distribution_number=chunk_section,chunk_number=0))
        self.selfs.update_chunk_info(nav_data['section_number'],nav_data["number"])
        # Update the display logic here based on nav_data
        self.selfs.update_bool_instructions()

