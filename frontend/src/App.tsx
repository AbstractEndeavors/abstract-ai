import { useState, useEffect, useCallback, useRef } from 'react';
import type { AppState, InstructionKey } from './types';
import { INSTRUCTION_KEYS } from './types';
import {
  fetchState,
  fetchModels,
  patchState,
  selectModel,
  submitQuery,
  fetchProgress,
  clearRequests,
  clearChunks,
  generateReadme,
  navTracker,
} from './api';
import ProgressFrame from './components/ProgressFrame';
import OutputOptions from './components/OutputOptions';
import PromptTabs from './components/PromptTabs';
import UtilityTabs from './components/UtilityTabs';

const DEFAULT_INSTRUCTION_BOOLS = Object.fromEntries(
  INSTRUCTION_KEYS.map(k => [k, false])
) as Record<InstructionKey, boolean>;

const DEFAULT_STATE: AppState = {
  request: '',
  prompt_data: '',
  chunk_data: '',
  query: '',
  instructions_text: '',
  instruction_bools: DEFAULT_INSTRUCTION_BOOLS,
  api: { header: '', api_key: '', api_env: '', endpoint: '' },
  model: { model_name: '', endpoint: '', max_tokens: 0 },
  models: [],
  role: 'user',
  response_type: 'text',
  prompt_percentage: 80,
  completion_percentage: 20,
  progress: {
    total_chunks: 0,
    current_chunk: 0,
    done: true,
    status_text: 'Ready',
    percentage: 0,
    query_count: 0,
  },
  urls: [],
  query_results: [],
  title: '',
  collate_responses: false,
  json_to_string: false,
  test_run: false,
  test_files: false,
  scan_mode_all: false,
  auto_chunk_title: false,
  reuse_chunk_data: false,
  append_chunks: false,
  response_key_options: [],
  feedback: {
    request_chunks: '',
    abort: '',
    additional_responses: '',
    suggestions: '',
    notation: '',
    other: '',
  },
  current_response: '',
  tracker: {
    instructions: 0,
    request: 0,
    prompt_data: 0,
    chunk: 0,
    query: 0,
    chunk_number: 0,
  },
  chunk_title: '',
  url_text: '',
};

function App() {
  const [appState, setAppState] = useState<AppState>(DEFAULT_STATE);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [responseIndex, setResponseIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load initial state
  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchState(), fetchModels()])
      .then(([state, modelsResp]) => {
        if (cancelled) return;
        setAppState(prev => ({
          ...prev,
          ...state,
          models: modelsResp.models.length > 0 ? modelsResp.models : state.models,
        }));
      })
      .catch(() => {
        // Backend not reachable yet — keep defaults
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  // Poll progress when a query is running
  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      try {
        const progress = await fetchProgress();
        setAppState(prev => ({ ...prev, progress }));
        if (progress.done) {
          clearInterval(pollRef.current!);
          pollRef.current = null;
          setIsSubmitting(false);
          // Refresh full state after completion
          fetchState()
            .then(state => setAppState(prev => ({ ...prev, ...state })))
            .catch(() => undefined);
        }
      } catch {
        clearInterval(pollRef.current!);
        pollRef.current = null;
        setIsSubmitting(false);
      }
    }, 1000);
  }, []);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleStateChange = useCallback((fields: Partial<AppState>) => {
    setAppState(prev => ({ ...prev, ...fields }));
    patchState(fields).catch(() => undefined);
  }, []);

  const handleInstructionBoolChange = useCallback((key: InstructionKey, value: boolean) => {
    setAppState(prev => {
      const updated = {
        ...prev,
        instruction_bools: { ...prev.instruction_bools, [key]: value },
      };
      patchState({ instruction_bools: updated.instruction_bools }).catch(() => undefined);
      return updated;
    });
  }, []);

  const handleModelSelect = useCallback((modelName: string) => {
    selectModel(modelName)
      .then(() => fetchState())
      .then(state => setAppState(prev => ({ ...prev, ...state })))
      .catch(() => undefined);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await submitQuery();
      startPolling();
    } catch {
      setIsSubmitting(false);
    }
  }, [isSubmitting, startPolling]);

  const handleClearRequests = useCallback(() => {
    clearRequests()
      .then(() => fetchState())
      .then(state => setAppState(prev => ({ ...prev, ...state })))
      .catch(() => undefined);
  }, []);

  const handleClearChunks = useCallback(() => {
    clearChunks()
      .then(() => fetchState())
      .then(state => setAppState(prev => ({ ...prev, ...state })))
      .catch(() => undefined);
  }, []);

  const handleGenReadme = useCallback(() => {
    generateReadme().catch(() => undefined);
  }, []);

  const handleTitleChange = useCallback((title: string) => {
    setAppState(prev => ({ ...prev, title }));
    patchState({ title }).catch(() => undefined);
  }, []);

  const handleNavPrev = useCallback(() => {
    setResponseIndex(i => Math.max(0, i - 1));
  }, []);

  const handleNavNext = useCallback(() => {
    setResponseIndex(i => Math.min(appState.query_results.length - 1, i + 1));
  }, [appState.query_results.length]);

  const handleNav = useCallback((key: string, value: number) => {
    if (value < 0) return;
    setAppState(prev => ({
      ...prev,
      tracker: { ...prev.tracker, [key]: value },
    }));
    navTracker(key, value)
      .then(() => fetchState())
      .then(state => setAppState(prev => ({ ...prev, ...state })))
      .catch(() => undefined);
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', color: '#aaa' }}>
        Loading Abstract AI...
      </div>
    );
  }

  return (
    <div className="app-root">
      <ProgressFrame
        progress={appState.progress}
        title={appState.title}
        onTitleChange={handleTitleChange}
        onNavPrev={handleNavPrev}
        onNavNext={handleNavNext}
        queryIndex={responseIndex}
        queryTotal={appState.query_results.length}
      />
      <OutputOptions
        onSubmit={handleSubmit}
        onClearRequests={handleClearRequests}
        onClearChunks={handleClearChunks}
        onGenReadme={handleGenReadme}
        isSubmitting={isSubmitting}
      />
      <div className="main-split">
        <div className="split-left">
          <PromptTabs
            request={appState.request}
            promptData={appState.prompt_data}
            chunkData={appState.chunk_data}
            query={appState.query}
            instructionsText={appState.instructions_text}
            instructionBools={appState.instruction_bools}
            tracker={appState.tracker}
            onRequestChange={v => handleStateChange({ request: v })}
            onPromptDataChange={v => handleStateChange({ prompt_data: v })}
            onChunkDataChange={v => handleStateChange({ chunk_data: v })}
            onQueryChange={v => handleStateChange({ query: v })}
            onInstructionsTextChange={v => handleStateChange({ instructions_text: v })}
            onInstructionBoolChange={handleInstructionBoolChange}
            onNav={handleNav}
          />
        </div>
        <div className="split-right">
          <UtilityTabs
            appState={appState}
            queryResults={appState.query_results}
            responseIndex={responseIndex}
            onStateChange={handleStateChange}
            onInstructionBoolChange={handleInstructionBoolChange}
            onModelSelect={handleModelSelect}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
