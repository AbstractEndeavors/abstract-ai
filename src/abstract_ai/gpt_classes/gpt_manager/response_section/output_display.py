from ..dependencies import *
def initialize_output_display(self)->None:
    """
    Initializes the display of the latest output in the GUI.
    """
    self.logger.info(f"initialize_output_display..")
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
    self.logger.info(f"determine_output_display..")
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
    self.logger.info(f"update_output..")
    if output_iteration < len(self.latest_output) and output_iteration >=0:
        self.current_output = self.latest_output[output_iteration]
        self.update_text_with_responses()
        
def adjust_output_display(self,num:int):
    self.logger.info(f"adjust_output_display..")
    self.response_text_number_actual+=num
    self.response_text_number_display+=num
    self.update_output(output_iteration=self.response_text_number_actual)
    self.window_mgr.update_value(key='-RESPONSE_TEXT_NUMBER-',value=self.response_text_number_display)
    
