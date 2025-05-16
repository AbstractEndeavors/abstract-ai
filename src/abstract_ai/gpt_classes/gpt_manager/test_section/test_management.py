from ..dependencies import *
#TestManagement
def check_test_bool(self)->None:
    """
    Checks the status of the `self.test_bool` attribute.

    `self.test_bool` is updated based on the user interaction with the testing tools interface.
    """
    if self.window_mgr.get_values():
        self.test_file_path = self.window_mgr.get_values()['-TEST_FILE_INPUT-']
        self.window_mgr.update_value('-TEST_FILE-',self.test_file_path)
        if self.event=='-TEST_RUN-':
            self.test_bool=self.window_mgr.get_values()['-TEST_RUN-']
            if self.test_bool:
                status_color = "green"
                value = 'TESTING'
                if self.test_file_path:
                    self.test_bool=os.path.isfile(self.test_file_path)
            else:
                status_color = "light blue"
                value = 'Awaiting Prompt'
            self.window_mgr.update_value(key='-PROGRESS_TEXT-', args={"value":value,"background_color":status_color})
            
def test_event_check(self)->bool:
    """
    Checks if a testing event has been triggered.

    A testing event is triggered when a user interacts with the testing features within the module.

    Returns:
        bool: True if a testing event has been triggered, otherwise False
    """
    if self.event in ['-TEST_RUN-','-TEST_FILES-']:
        self.check_test_bool()
    else:
        return False
    return True

