from .prompt_tabs import prompt_tabs
from .progress_frame import get_progress_frame,get_output_options
from .gui_utilities import utilities
from .gui_utils import *
def get_total_layout()->list:
    return [
        [get_progress_frame()],
        [get_output_options()],
        [prompt_tabs(),get_column([utilities()])]
        ]

