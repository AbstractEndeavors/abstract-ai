import os
import re

def modify_imports(root_directory, pattern_js, conversion_type='imports'):
    
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        contents = file.read()

                    for pattern in pattern_js:
                        contents = contents.replace(pattern[conversion_type], pattern[convert_js[conversion_type]])

                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(contents)
                except IOError as e:
                    print(f"Error processing file {file_path}: {e}")
froms="""C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/__init__.py
from .gpt_classes import *
from gpt_classes.__init__ import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/__init__.py
from .gui_components import *
from gui_components.__init__ import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/abstract_ai_gui_backend.py
from . import 
from __init__ import 

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/abstract_ai_gui.py
from .abstract_ai_gui_shared  import *
from abstract_ai_gui_shared  import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/abstract_ai_gui_shared.py
from .multiline_slider 
from multiline_slider

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/abstract_ai_gui_shared.py
from . import 
from abstract_ai import

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/generate_readme.py
from .multiline_slider
from multiline_slider

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/multiline_slider.py
from .abstract_ai_gui_shared
from abstract_ai_gui_shared

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/__init__.py
from .abstract_ai_gui import *
from abstract_ai_gui import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/__init__.py
from .generate_readme import read_me_window
from generate_readme import read_me_window

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gui_components/__init__.py
from .multiline_slider import MultilineSlider
from multiline_slider import MultilineSlider

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .api_selection.ApiBuilder import *
from api_selection.ApiBuilder import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .model_selection.ModelBuilder import *
from model_selection.ModelBuilder import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .prompt_selection.PromptBuilder import *
from prompt_selection.PromptBuilder import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .response_selection.ResponseBuilder import *
from response_selection.ResponseBuilder import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .instruction_selection.InstructionBuilder import *
from instruction_selection.InstructionBuilder import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/__init__.py
from .file_section.JsonHandler import *
from file_section.JsonHandler import *

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/prompt_selection/PromptBuilder.py
from ..instruction_selection.InstructionBuilder import InstructionManager
from abstract_ai import InstructionManager

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/prompt_selection/PromptBuilder.py
from ..model_selection.ModelBuilder import ModelManager
from abstract_ai import ModelManager

C:/Users/jrput/Documents/python projects/Modules/abstract_ai/src/abstract_ai/gpt_classes/prompt_selection/PromptBuilder.py
from . import *
from __init__ import *
"""
json_reference = []
conversion_type="module"
froms = froms.split('\n\n')
for each in froms:
    spl = each.split('\n')
    json_reference.append({"file":spl[0],"module":spl[1],"imports":spl[2]})
for each in json_reference:
    file_path=each["file"]
    convert_js = {'module': 'imports', 'imports': 'module'}
    with open(file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    print(each[conversion_type],each[convert_js[conversion_type]])
    contents = contents.replace(each[conversion_type], each[convert_js[conversion_type]])
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(contents)


