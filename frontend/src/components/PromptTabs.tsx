import React, { useState } from 'react';
import NavigationBar from './NavigationBar';
import type { AppState, InstructionKey, InstructionBools } from '../types';
import { INSTRUCTION_KEYS } from '../types';

type PromptTabId = 'request' | 'prompt_data' | 'chunks' | 'query' | 'instructions';

interface PromptTabsProps {
  request: string;
  promptData: string;
  chunkData: string;
  query: string;
  instructionsText: string;
  instructionBools: InstructionBools;
  tracker: AppState['tracker'];
  onRequestChange: (v: string) => void;
  onPromptDataChange: (v: string) => void;
  onChunkDataChange: (v: string) => void;
  onQueryChange: (v: string) => void;
  onInstructionsTextChange: (v: string) => void;
  onInstructionBoolChange: (key: InstructionKey, v: boolean) => void;
  onNav: (key: string, value: number) => void;
}

const TAB_LABELS: { id: PromptTabId; label: string }[] = [
  { id: 'request', label: 'REQUEST' },
  { id: 'prompt_data', label: 'PROMPT DATA' },
  { id: 'chunks', label: 'CHUNKS' },
  { id: 'query', label: 'QUERY' },
  { id: 'instructions', label: 'INSTRUCTIONS' },
];

// Instruction keys shown in the INSTRUCTIONS tab checkbox grid (exclude 'instructions' itself)
const INSTRUCTION_GRID_KEYS = INSTRUCTION_KEYS.filter(k => k !== 'instructions') as InstructionKey[];

function formatLabel(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

const PromptTabs: React.FC<PromptTabsProps> = ({
  request,
  promptData,
  chunkData,
  query,
  instructionsText,
  instructionBools,
  tracker,
  onRequestChange,
  onPromptDataChange,
  onChunkDataChange,
  onQueryChange,
  onInstructionsTextChange,
  onInstructionBoolChange,
  onNav,
}) => {
  const [activeTab, setActiveTab] = useState<PromptTabId>('request');

  const navInfoMap: Record<PromptTabId, { key: string; current: number; total: number }> = {
    request: { key: 'request', current: tracker.request, total: 0 },
    prompt_data: { key: 'prompt_data', current: tracker.prompt_data, total: 0 },
    chunks: { key: 'chunk', current: tracker.chunk, total: 0 },
    query: { key: 'query', current: tracker.query, total: 0 },
    instructions: { key: 'instructions', current: tracker.instructions, total: 0 },
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'request':
        return (
          <>
            <NavigationBar
              label="Request"
              current={tracker.request}
              total={0}
              onPrev={() => onNav('request', tracker.request - 1)}
              onNext={() => onNav('request', tracker.request + 1)}
            />
            <textarea
              className="tab-textarea"
              value={request}
              onChange={e => onRequestChange(e.target.value)}
              placeholder="Enter request..."
            />
          </>
        );
      case 'prompt_data':
        return (
          <>
            <NavigationBar
              label="Prompt Data"
              current={tracker.prompt_data}
              total={0}
              onPrev={() => onNav('prompt_data', tracker.prompt_data - 1)}
              onNext={() => onNav('prompt_data', tracker.prompt_data + 1)}
            />
            <textarea
              className="tab-textarea"
              value={promptData}
              onChange={e => onPromptDataChange(e.target.value)}
              placeholder="Enter prompt data..."
            />
          </>
        );
      case 'chunks':
        return (
          <>
            <NavigationBar
              label="Chunk"
              current={tracker.chunk}
              total={0}
              onPrev={() => onNav('chunk', tracker.chunk - 1)}
              onNext={() => onNav('chunk', tracker.chunk + 1)}
            />
            <textarea
              className="tab-textarea"
              value={chunkData}
              onChange={e => onChunkDataChange(e.target.value)}
              placeholder="Chunk data..."
            />
          </>
        );
      case 'query':
        return (
          <>
            <NavigationBar
              label="Query"
              current={tracker.query}
              total={0}
              onPrev={() => onNav('query', tracker.query - 1)}
              onNext={() => onNav('query', tracker.query + 1)}
            />
            <textarea
              className="tab-textarea"
              value={query}
              onChange={e => onQueryChange(e.target.value)}
              placeholder="Enter query..."
            />
          </>
        );
      case 'instructions':
        return (
          <>
            <NavigationBar
              label="Instructions"
              current={tracker.instructions}
              total={0}
              onPrev={() => onNav('instructions', tracker.instructions - 1)}
              onNext={() => onNav('instructions', tracker.instructions + 1)}
            />
            <textarea
              className="tab-textarea"
              style={{ flex: '0 0 120px', minHeight: '120px' }}
              value={instructionsText}
              onChange={e => onInstructionsTextChange(e.target.value)}
              placeholder="Enter instructions..."
            />
            <div className="checkbox-grid">
              {INSTRUCTION_GRID_KEYS.map(key => (
                <label key={key} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={instructionBools[key]}
                    onChange={e => onInstructionBoolChange(key, e.target.checked)}
                  />
                  {formatLabel(key)}
                </label>
              ))}
            </div>
          </>
        );
    }
  };

  // suppress unused variable warning
  void navInfoMap;

  return (
    <div className="tabs-container">
      <div className="tab-bar">
        {TAB_LABELS.map(({ id, label }) => (
          <button
            key={id}
            className={`tab-btn${activeTab === id ? ' active' : ''}`}
            onClick={() => setActiveTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default PromptTabs;
