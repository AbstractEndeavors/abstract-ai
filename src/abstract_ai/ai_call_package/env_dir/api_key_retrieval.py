import json,os
from abstract_security import *
OPENAI_BASE="OPENAI"
GROK_BASE="GROK"
GEMINI_BASE="GEMINI"
KEY_BASE="API_KEY"
AI_SELECT_JS={"openai":OPENAI_BASE,"grok":GROK_BASE,"gemini":GEMINI_BASE}
def get_abs_path():
    return os.path.abspath(__file__)
def get_abs_dir():
    abs_path = get_abs_path()
    return os.path.dirname(abs_path)
def get_env_path():
    abs_dir = get_abs_dir()
    return os.path.join(abs_dir,'.env')
def get_ai_api_key_value(key,path=None):
    return get_env_value(key=key,path=path)
def get_exact_char(char, i, word):
    if i < len(word) and word[i] == char:
        return char
    return None

def extract_consistent_chars(word, comp_word):
    const_chars = []
    current_seq = ""
    for i, char in enumerate(comp_word):
        exact_char = get_exact_char(char, i, word)
        if exact_char:
            current_seq += exact_char
        else:
            if current_seq:
                const_chars.append(current_seq)
                current_seq = ""
    if current_seq:
        const_chars.append(current_seq)
    return const_chars if const_chars else [""]

def get_most_similar(keyword, words):
    # Normalize inputs
    keyword = keyword.lower().replace("_", "")
    words_lower = {word.lower().replace("_", ""): word for word in words}

    # Check exact match (with underscore handling)
    for orig_word in words:
        if keyword.replace("_", "") == orig_word.lower().replace("_", ""):
            return orig_word

    # Find best match based on substring or similarity
    best_match = None
    max_score = -1

    for key_lower, orig_word in words_lower.items():
        # Extract consistent character sequences
        consistent = extract_consistent_chars(keyword, key_lower)
        # Score based on total length of matching sequences
        score = sum(len(seq) for seq in consistent)
        
        # Alternative: Check if keyword is a substring (ignoring underscores)
        if keyword in key_lower or any(keyword in seq for seq in consistent):
            score += len(keyword) * 2  # Boost for substring matches
        
        if score > max_score:
            max_score = score
            best_match = orig_word

    return best_match if best_match else keyword
        
def get_correct_json_key(dict_obj,key):
    similar_key = dict_obj.get(key)
    if not similar_key:
        keys = list(dict_obj.keys())
        similar_key = get_most_similar(key, keys)
    return similar_key
def get_key_type(key,typ=None):
    typ=typ or ''
    if typ:
        add_type = f"_{typ.upper()}"
        if not key.endswith(add_type):
            key = f"{key}{add_type}"
    return key
def get_correct_ai_key(ai=None):
    ai = ai or 'openai'
    ai = get_correct_json_key(AI_SELECT_JS,ai)
    return ai
def get_base_ai_key(ai=None):
    ai = get_correct_ai_key(ai)
    ai = ai or OPENAI_BASE
    return f"{ai}_{KEY_BASE}"
def get_ai_api_key(ai=None,typ=None):
    base_ai_key = get_base_ai_key(ai)
    if typ:
        base_ai_key = get_key_type(base_ai_key,typ)
    return get_ai_api_key_value(base_ai_key)
def get_grok_key(typ=None):
    return get_ai_api_key(ai='grok')
def get_grok_bot_key():
    return get_ai_api_key(ai='grok',typ='bot')
def get_openai_key(typ=None):
    return get_ai_api_key(ai='openai')
def get_openai_bot_key():
    return get_ai_api_key(ai='openai',typ='bot')
def get_gemini_key(typ=None):
    return get_ai_api_key(ai='gemini')
def get_gemini_bot_key():
    return get_ai_api_key(ai='gemini',typ='bot')

