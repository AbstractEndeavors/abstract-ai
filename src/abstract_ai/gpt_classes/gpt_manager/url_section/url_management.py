from ..dependencies import *
def append_output(self,key:str,new_content:str)->None:
    """
    appends a line of text to the 'other' section of feedback on the GUI.
    """
    self.window_mgr.update_value(key=key,value=self.window_mgr.get_from_value(key)+'\n\n'+new_content)
    
def get_url(self)->None:
    """
    retrieves the URL entered by the user in the corresponding input field of the UI.
    """
    url = self.window_mgr.get_values()['-URL-']
    if url==None:
        url_list =self.window_mgr.get_values()['-URL_LIST-']
        url = safe_list_return(url_list)
    return url

def get_url_manager(self,url:str=None)->str:
    """
    returns the processed URL. It uses the UrlManager and SafeRequest classes from the abstract_webtools
    module to process and safe-proof the URL.
    """
    url = url or self.get_url()
    url_manager = UrlManager(url=url)    
    return url_manager

def url_event_check(self)->bool:
    """
    Checks if a URL event has been triggered.

    An event is triggered when a user interacts with the URL management interface.
    This function prompts the SafeRequest module to return the HTML content or the
    BeautifulSoup object of the specified URL.

    Returns:
        bool: True if a URL event has been triggered, otherwise False
    """
    if self.event in ['-GET_SOUP-',
                      '-GET_SOURCE_CODE-',
                      '-ADD_URL-']:
        url_manager = self.get_url_manager()
        if self.event in ['-GET_SOUP-',
                          '-GET_SOURCE_CODE-']:
            self.chunk_title=None
            data=self.window_mgr.get_values()['-URL_TEXT-']
            url=None
            if url_manager.url:
                url = url_manager.url
            if self.event=='-GET_SOUP-':
                self.url_chunk_type='SOUP'
                data = url_grabber_component(url=url)
                self.window_mgr.update_value(key='-URL_TEXT-',value=data)
            elif url_manager.url and self.event=='-GET_SOURCE_CODE-':
                url_list =self.window_mgr.get_values()['-URL_LIST-']
                if url_list:
                    url = UrlManager(url=self.window_mgr.get_values()['-URL_LIST-'][0]).url
                    self.chunk_title=url
                    self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-',section='url'),value=url)
                request_manager = SafeRequest(url_manager=url_manager)
                if self.event == '-GET_SOURCE_CODE-':
                    self.url_chunk_type='URL'
                    data = request_manager.source_code
            else:
                print(f'url {url} is malformed... aborting...')
        elif self.event == '-ADD_URL-':
            url = url_manager.url
            url_list = make_list(self.window_mgr.get_values()['-URL_LIST-']) or make_list(url)
            if url_list:
                if url not in url_list:
                    url_list.append(url)
            self.window_mgr.update_value(key='-URL_LIST-',args={"values":url_list})
    else:
        return False
    return True

