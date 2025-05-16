import os
import PySimpleGUI as sg
from abstract_gui import *
from .gui_utils import *
from abstract_utilities import get_closest_match_from_list
from abstract_utilities.list_utils import ensure_nested_list,find_original_case
from abstract_utilities.class_utils import get_all_functions_for_instance,get_all_params,get_fun
class GuiUtilsManager:
    def __init__(self):
        # Mapping between Python PySimpleGUI components and their HTML/JS counterparts
        self.component_mappings = {
            "Button": lambda args: f'<button>{args.get("button_text", "Button")}</button>',
            "InputText": lambda args: f'<input type="text" value="{args.get("default_text", "")}" style="background-color:{args.get("background_color", "white")};" />',
            "Input": lambda args: f'<input type="text" value="{args.get("default_text", "")}" />',
            "ProgressBar": lambda args: f'<progress max="{args.get("max_value", 100)}" value="{args.get("default_value", 0)}"></progress>',
            "Frame": lambda args: f'<fieldset><legend>{args.get("title", "")}</legend>{args.get("layout", "")}</fieldset>'
            # Add other component mappings as needed
        }

    def make_component(self, component_type, *args, output_language='python', **kwargs):
        if output_language == 'javascript':
            if component_type in self.component_mappings:
                return self.component_mappings[component_type](kwargs)
            else:
                raise ValueError(f"Component {component_type} not supported for JavaScript.")
        
        # Else return Python PySimpleGUI component
        return self.make_pysimplegui_component(component_type, *args, **kwargs)

    def make_pysimplegui_component(self, component_type, *args, **kwargs):
        # Example: Mapping to PySimpleGUI components
        if component_type == 'Button':
            return sg.Button(*args, **kwargs)
        elif component_type == 'InputText':
            return sg.InputText(*args, **kwargs)
        elif component_type == 'ProgressBar':
            return sg.ProgressBar(*args, **kwargs)
        elif component_type == 'Frame':
            return sg.Frame(*args, **kwargs)
        # Add more PySimpleGUI component mappings as needed



def get_progress_frame()->list:
    return [
        [
            make_component("Frame", 'PROGRESS', layout=[
                [
                    make_component("InputText", 'Awaiting Prompt', key='-PROGRESS_TEXT-', background_color="light blue", auto_size_text=True, size=(20, 20)),
                    make_component("ProgressBar", 100, orientation='h', size=(10, 20), key='-PROGRESS-'),
                    make_component("Input", default_text='0', key=text_to_key("query count"), size=(30, 20), disabled=True, enable_events=True)
                ]
            ]),
            make_component("Frame", 'query title', layout=[
                [
                    make_component("Input", default_text="title of prompt", size=(30, 1), key=text_to_key('title input'))
                ]
            ]),
            make_component('Frame', "response nav", [
                get_left_right_nav(name='response text',section=False,push=False)
            ])
        ]
    ]
####submit options
def get_output_options()->list:
    return [
        [
         make_component("Button",button_text="SUBMIT QUERY",key="-SUBMIT_QUERY-", disabled=False,enable_evete=True),
         make_component("Button",button_text="CLEAR REQUESTS",key='-CLEAR_REQUESTS-', disabled=False,enable_evete=True),
         make_component("Button",button_text="CLEAR CHUNKS",key='-CLEAR_CHUNKS-', disabled=False,enable_evete=True),
         make_component("Button",button_text="GEN README",key='-GENERATE_README-', disabled=False,enable_evete=True)]
    ]

