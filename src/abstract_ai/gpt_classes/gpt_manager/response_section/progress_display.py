from ..dependencies import *
def get_dots(self)->None:
    """
    This is a helper method used in the update_progress_chunks method. It manages the progress tracking visual
    indication in the UI. It updates the dots string depending on the current state of the dots. If the dots string
    is full of dots, it resets it to empty.
    """
    self.logger.info(f"get_dots..")
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
    self.logger.info(f"update_progress_chunks..")
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
