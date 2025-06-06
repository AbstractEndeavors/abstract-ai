XAI_MODELS = [
    {'model': 'grok-3-beta', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'grok-3-fast-beta', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'grok-3-mini-beta', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'grok-3-mini-fast-beta', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'grok-2-1212', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'grok-2-vision-1212', 'endpoint': 'https://api.x.ai/v1/chat/completions', 'tokens': 8192},
    {'model': 'v1', 'endpoint': 'https://api.x.ai/v1/embeddings', 'tokens': None},
    {'model': 'grok-2-image', 'endpoint': 'https://api.x.ai/v1/images/generations', 'tokens': None}
]

OPENAI_MODELS = [{'model': 'whisper-1', 'endpoint': 'https://api.openai.com/v1/audio/transcriptions', 'tokens': None},
                    {'model': 'gpt-4o', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 4097},
                       {'model': 'gpt-4', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 8192},
                       {'model': 'gpt-4-0613', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 8192},
                       {'model': 'gpt-4-32k', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 32768},
                       {'model': 'gpt-4-32k-0613', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 32768},
                       {'model': 'gpt-3.5-turbo', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 8001},
                       {'model': 'gpt-3.5-turbo-0613', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 4097},
                       {'model': 'gpt-3.5-turbo-16k', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 16385},
                       {'model': 'gpt-3.5-turbo-16k-0613', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 16385},
                       {'model': 'gpt-3.5-turbo-instruct', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 4097},
                       {'model': 'babbage-002', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 16384},
                       {'model': 'davinci-002', 'endpoint': 'https://api.openai.com/v1/chat/completions', 'tokens': 16384},
                       {'model': 'text-embedding-ada-002', 'endpoint': 'https://api.openai.com/v1/embeddings', 'tokens': None},
                       {'model': 'gpt-3.5-turbo', 'endpoint': 'https://api.openai.com/v1/fine_tuning/jobs', 'tokens': 8001},
                       {'model': 'babbage-002', 'endpoint': 'https://api.openai.com/v1/fine_tuning/jobs', 'tokens': 16384},
                       {'model': 'davinci-002', 'endpoint': 'https://api.openai.com/v1/fine_tuning/jobs', 'tokens': 16384},
                       {'model': 'text-moderation-stable', 'endpoint': 'https://api.openai.com/v1/moderations', 'tokens': 2049},
                       {'model': 'text-moderation-latest', 'endpoint': 'https://api.openai.com/v1/moderations', 'tokens': 2049}]
