# DEPENDENCIES #

import pyperclip,asyncio,threading,logging,os
from ...gui_components.abstract_ai_gui_shared import get_total_layout,instructions_keys, all_token_keys, test_options_keys
from ...gui_components.generate_readme import read_me_window
from ...gui_components.abstract_ai_gui_navigation import AbstractNavigationManager
from ...gpt_classes import ApiManager,InstructionManager,ResponseManager,PromptManager,ModelManager
from ...specializations import FileCollator,read_from_file_with_multiple_encodings
from ...specializations.database_query import get_auto_db_query
from ...specializations.responseContentParser import *
from abstract_webtools import urlManager, requestManager
from abstract_webtools.url_grabber import url_grabber_component
from abstract_gui import (
    get_event_key_js,
    text_to_key,
    AbstractWindowManager,
    NextReadManager,
    expandable,
    AbstractBrowser)
from abstract_utilities import (
    get_any_value,
    create_new_name,
    get_sleep,
    eatAll,
    safe_json_loads,
    read_from_file,
    make_list,
    ThreadManager,
    HistoryManager,
    get_file_create_time,
    safe_read_from_json,
    is_number,
    format_json_key_values
)
logging.basicConfig(
    level=logging.INFO,                     # Set the logging level (INFO, in this case)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler()             # Also log to the console (optional)
    ]
)
logger = logging.getLogger(__name__)
