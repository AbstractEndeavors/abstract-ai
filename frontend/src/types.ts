export const INSTRUCTION_KEYS = [
  'instructions',
  'additional_responses',
  'suggestions',
  'abort',
  'database_query',
  'notation',
  'generate_title',
  'additional_instruction',
  'request_chunks',
  'prompt_as_previous',
  'token_adjustment',
] as const;

export type InstructionKey = typeof INSTRUCTION_KEYS[number];

export type InstructionBools = Record<InstructionKey, boolean>;

export interface Progress {
  total_chunks: number;
  current_chunk: number;
  done: boolean;
  status_text: string;
  percentage: number;
  query_count: number;
}

export interface ModelConfig {
  model_name: string;
  endpoint: string;
  max_tokens: number;
}

export interface Tracker {
  instructions: number;
  request: number;
  prompt_data: number;
  chunk: number;
  query: number;
  chunk_number: number;
}

export interface Feedback {
  request_chunks: string;
  abort: string;
  additional_responses: string;
  suggestions: string;
  notation: string;
  other: string;
}

export interface AppState {
  request: string;
  prompt_data: string;
  chunk_data: string;
  query: string;
  instructions_text: string;
  instruction_bools: InstructionBools;
  api: { header: string; api_key: string; api_env: string; endpoint: string };
  model: ModelConfig;
  models: string[];
  role: string;
  response_type: string;
  prompt_percentage: number;
  completion_percentage: number;
  progress: Progress;
  urls: string[];
  query_results: QueryResult[];
  title: string;
  collate_responses: boolean;
  json_to_string: boolean;
  test_run: boolean;
  test_files: boolean;
  scan_mode_all: boolean;
  auto_chunk_title: boolean;
  reuse_chunk_data: boolean;
  append_chunks: boolean;
  response_key_options: string[];
  feedback: Feedback;
  current_response: string;
  tracker: Tracker;
  chunk_title: string;
  url_text: string;
}

export interface QueryResult {
  model: string;
  title: string;
  request: string;
  response_content: string;
  api_response: string;
  file_path: string;
}
