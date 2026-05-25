import React, { useState } from 'react';
import type { AppState, InstructionKey, QueryResult } from '../types';
import { INSTRUCTION_KEYS } from '../types';
import { addUrl, deleteUrl, fetchUrl } from '../api';

type UtilTabId = 'settings' | 'responses' | 'files' | 'query_tab' | 'urls' | 'feedback';

interface UtilityTabsProps {
  appState: AppState;
  queryResults: QueryResult[];
  responseIndex: number;
  onStateChange: (fields: Partial<AppState>) => void;
  onInstructionBoolChange: (key: InstructionKey, value: boolean) => void;
  onModelSelect: (modelName: string) => void;
}

const RESPONSE_TYPES = ['instruction', 'json', 'bash', 'text'];
const ROLES = ['user', 'assistant', 'system'];

const TAB_LABELS: { id: UtilTabId; label: string }[] = [
  { id: 'settings', label: 'SETTINGS' },
  { id: 'responses', label: 'RESPONSES' },
  { id: 'files', label: 'FILES' },
  { id: 'query_tab', label: 'QUERY' },
  { id: 'urls', label: 'URLS' },
  { id: 'feedback', label: 'FEEDBACK' },
];

function formatLabel(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function pctOptions(): number[] {
  const opts: number[] = [];
  for (let i = 0; i <= 100; i += 5) opts.push(i);
  return opts;
}

const UtilityTabs: React.FC<UtilityTabsProps> = ({
  appState,
  queryResults,
  responseIndex,
  onStateChange,
  onInstructionBoolChange,
  onModelSelect,
}) => {
  const [activeTab, setActiveTab] = useState<UtilTabId>('settings');
  const [urlInput, setUrlInput] = useState('');
  const [selectedUrl, setSelectedUrl] = useState('');
  const [urlContent, setUrlContent] = useState('');
  const [dbQuery, setDbQuery] = useState(false);
  const [performQuery, setPerformQuery] = useState(false);

  const handleAddUrl = async () => {
    const url = urlInput.trim();
    if (!url) return;
    await addUrl(url);
    onStateChange({ urls: [...appState.urls, url] });
    setUrlInput('');
  };

  const handleDeleteUrl = async (url: string) => {
    await deleteUrl(url);
    onStateChange({ urls: appState.urls.filter(u => u !== url) });
    if (selectedUrl === url) setSelectedUrl('');
  };

  const handleFetchUrl = async (type: 'soup' | 'source') => {
    if (!selectedUrl) return;
    try {
      const result = await fetchUrl(selectedUrl, type);
      setUrlContent(result.content ?? '');
    } catch {
      setUrlContent('Error fetching URL.');
    }
  };

  const currentResponse = queryResults[responseIndex] ?? null;

  const renderSettings = () => (
    <div className="settings-scroll">
      {/* Token Percentages */}
      <section className="settings-section">
        <div className="section-title">Token Percentages</div>
        <div className="settings-row">
          <label>Prompt %</label>
          <select
            value={appState.prompt_percentage}
            onChange={e => onStateChange({ prompt_percentage: Number(e.target.value) })}
            className="settings-select"
          >
            {pctOptions().map(n => <option key={n} value={n}>{n}</option>)}
          </select>
          <label>Completion %</label>
          <select
            value={appState.completion_percentage}
            onChange={e => onStateChange({ completion_percentage: Number(e.target.value) })}
            className="settings-select"
          >
            {pctOptions().map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </section>

      {/* API Options */}
      <section className="settings-section">
        <div className="section-title">API Options</div>
        <div className="settings-col">
          <div className="settings-row">
            <label>Header</label>
            <input
              type="text"
              className="settings-input"
              value={appState.api.header}
              onChange={e => onStateChange({ api: { ...appState.api, header: e.target.value } })}
            />
          </div>
          <div className="settings-row">
            <label>API Key</label>
            <input
              type="text"
              className="settings-input"
              value={appState.api.api_key}
              onChange={e => onStateChange({ api: { ...appState.api, api_key: e.target.value } })}
            />
          </div>
          <div className="settings-row">
            <label>API Env</label>
            <input
              type="text"
              className="settings-input"
              value={appState.api.api_env}
              onChange={e => onStateChange({ api: { ...appState.api, api_env: e.target.value } })}
            />
          </div>
        </div>
      </section>

      {/* Type Options */}
      <section className="settings-section">
        <div className="section-title">Type Options</div>
        <div className="settings-row">
          <label>Role</label>
          <select
            value={appState.role}
            onChange={e => onStateChange({ role: e.target.value })}
            className="settings-select"
          >
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <label>Response Type</label>
          <select
            value={appState.response_type}
            onChange={e => onStateChange({ response_type: e.target.value })}
            className="settings-select"
          >
            {RESPONSE_TYPES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </section>

      {/* Model Selection */}
      <section className="settings-section">
        <div className="section-title">Model Selection</div>
        <div className="settings-col">
          <div className="settings-row">
            <label>Model</label>
            <select
              value={appState.model.model_name}
              onChange={e => onModelSelect(e.target.value)}
              className="settings-select"
              style={{ flex: 1 }}
            >
              {appState.models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="settings-row">
            <label>Endpoint</label>
            <input
              type="text"
              className="settings-input"
              value={appState.model.endpoint}
              readOnly
            />
          </div>
          <div className="settings-row">
            <label>Max Tokens</label>
            <input
              type="text"
              className="settings-input"
              value={appState.model.max_tokens}
              readOnly
            />
          </div>
        </div>
      </section>

      {/* Enable Instructions */}
      <section className="settings-section">
        <div className="section-title">Enable Instructions</div>
        <div className="checkbox-grid">
          {INSTRUCTION_KEYS.map(key => (
            <label key={key} className="checkbox-label">
              <input
                type="checkbox"
                checked={appState.instruction_bools[key]}
                onChange={e => onInstructionBoolChange(key, e.target.checked)}
              />
              {formatLabel(key)}
            </label>
          ))}
        </div>
      </section>

      {/* Test Tools */}
      <section className="settings-section">
        <div className="section-title">Test Tools</div>
        <div className="settings-col">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.test_run}
              onChange={e => onStateChange({ test_run: e.target.checked })}
            />
            Test Run
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.test_files}
              onChange={e => onStateChange({ test_files: e.target.checked })}
            />
            Test Files
          </label>
          <div className="settings-row" style={{ marginTop: '6px' }}>
            <input type="text" className="settings-input" placeholder="File path..." style={{ flex: 1 }} />
            <button className="action-btn" style={{ padding: '4px 8px' }}>Browse</button>
          </div>
        </div>
      </section>

      {/* File Options */}
      <section className="settings-section">
        <div className="section-title">File Options</div>
        <div className="checkbox-grid">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.auto_chunk_title}
              onChange={e => onStateChange({ auto_chunk_title: e.target.checked })}
            />
            Auto Chunk Title
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.reuse_chunk_data}
              onChange={e => onStateChange({ reuse_chunk_data: e.target.checked })}
            />
            Reuse Chunk Data
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.append_chunks}
              onChange={e => onStateChange({ append_chunks: e.target.checked })}
            />
            Append Chunks
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={appState.scan_mode_all}
              onChange={e => onStateChange({ scan_mode_all: e.target.checked })}
            />
            Scan Mode All
          </label>
        </div>
      </section>
    </div>
  );

  const renderResponses = () => (
    <div className="tab-content-inner">
      <div className="settings-row" style={{ gap: '16px', marginBottom: '8px' }}>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={appState.collate_responses}
            onChange={e => onStateChange({ collate_responses: e.target.checked })}
          />
          Collate Responses
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={appState.json_to_string}
            onChange={e => onStateChange({ json_to_string: e.target.checked })}
          />
          JSON to String
        </label>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ color: '#aaa', fontSize: '12px' }}>Response Key</label>
          <select className="settings-select">
            {appState.response_key_options.map(k => <option key={k} value={k}>{k}</option>)}
          </select>
        </div>
      </div>
      <textarea
        className="tab-textarea"
        value={currentResponse?.response_content ?? ''}
        readOnly
        placeholder="Response content will appear here..."
      />
    </div>
  );

  const renderFiles = () => (
    <div className="tab-content-inner">
      <div className="settings-row" style={{ marginBottom: '8px', gap: '8px' }}>
        <label style={{ color: '#aaa', fontSize: '12px' }}>Chunk Title</label>
        <input
          type="text"
          className="settings-input"
          value={appState.chunk_title}
          onChange={e => onStateChange({ chunk_title: e.target.value })}
          style={{ flex: 1 }}
        />
      </div>
      <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
        <button className="action-btn">CHUNK DATA</button>
        <button className="action-btn">RESPONSE DATA</button>
      </div>
      <textarea
        className="tab-textarea"
        placeholder="File content..."
        readOnly
      />
    </div>
  );

  const renderQuery = () => (
    <div className="tab-content-inner">
      <div className="settings-row" style={{ gap: '16px', marginBottom: '8px' }}>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={dbQuery}
            onChange={e => setDbQuery(e.target.checked)}
          />
          Database Query
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={performQuery}
            onChange={e => setPerformQuery(e.target.checked)}
          />
          Perform Query
        </label>
      </div>
      <div className="settings-row" style={{ marginBottom: '8px', gap: '8px' }}>
        <label style={{ color: '#aaa', fontSize: '12px' }}>Table</label>
        <select className="settings-select" style={{ flex: 1 }}>
          <option value="">-- select table --</option>
        </select>
      </div>
      <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
        <button className="action-btn">CHUNK DATA</button>
        <button className="action-btn">RESPONSE DATA</button>
      </div>
      <textarea
        className="tab-textarea"
        placeholder="Query results..."
        readOnly
      />
    </div>
  );

  const renderUrls = () => (
    <div className="tab-content-inner">
      <div className="settings-row" style={{ gap: '8px', marginBottom: '8px' }}>
        <input
          type="text"
          className="settings-input"
          value={urlInput}
          onChange={e => setUrlInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleAddUrl(); }}
          placeholder="Enter URL..."
          style={{ flex: 1 }}
        />
        <button className="action-btn" onClick={handleAddUrl}>Add URL</button>
      </div>
      <div className="url-list">
        {appState.urls.map(url => (
          <div
            key={url}
            className={`url-item${selectedUrl === url ? ' selected' : ''}`}
            onClick={() => setSelectedUrl(url)}
          >
            <span className="url-text">{url}</span>
            <button
              className="url-delete-btn"
              onClick={e => { e.stopPropagation(); handleDeleteUrl(url); }}
            >
              &#x2715;
            </button>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '8px', margin: '8px 0' }}>
        <button className="action-btn" onClick={() => handleFetchUrl('soup')}>GET SOUP</button>
        <button className="action-btn" onClick={() => handleFetchUrl('source')}>GET SOURCE</button>
        <button className="action-btn">CHUNK DATA</button>
      </div>
      <div className="settings-row" style={{ gap: '8px', marginBottom: '8px' }}>
        <label style={{ color: '#aaa', fontSize: '12px' }}>Chunk Title</label>
        <input
          type="text"
          className="settings-input"
          value={appState.chunk_title}
          onChange={e => onStateChange({ chunk_title: e.target.value })}
          style={{ flex: 1 }}
        />
      </div>
      <textarea
        className="tab-textarea"
        value={urlContent}
        readOnly
        placeholder="Fetched content will appear here..."
      />
    </div>
  );

  const renderFeedback = () => (
    <div className="tab-content-inner">
      <label style={{ color: '#aaa', fontSize: '11px', marginBottom: '4px' }}>Current Response (read-only)</label>
      <textarea
        className="tab-textarea"
        style={{ flex: '0 0 80px', minHeight: '80px' }}
        value={appState.current_response}
        readOnly
        placeholder="Current response..."
      />
      <div className="feedback-grid">
        <div className="feedback-field">
          <label>Request Chunks</label>
          <input
            type="text"
            className="settings-input"
            value={appState.feedback.request_chunks}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, request_chunks: e.target.value } })}
          />
        </div>
        <div className="feedback-field">
          <label>Abort</label>
          <input
            type="text"
            className="settings-input"
            value={appState.feedback.abort}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, abort: e.target.value } })}
          />
        </div>
        <div className="feedback-field">
          <label>Additional Responses</label>
          <input
            type="text"
            className="settings-input"
            value={appState.feedback.additional_responses}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, additional_responses: e.target.value } })}
          />
        </div>
        <div className="feedback-field">
          <label>Suggestions</label>
          <textarea
            className="tab-textarea"
            style={{ minHeight: '60px', flex: '0 0 60px' }}
            value={appState.feedback.suggestions}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, suggestions: e.target.value } })}
          />
        </div>
        <div className="feedback-field">
          <label>Notation</label>
          <textarea
            className="tab-textarea"
            style={{ minHeight: '60px', flex: '0 0 60px' }}
            value={appState.feedback.notation}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, notation: e.target.value } })}
          />
        </div>
        <div className="feedback-field">
          <label>Other</label>
          <textarea
            className="tab-textarea"
            style={{ minHeight: '60px', flex: '0 0 60px' }}
            value={appState.feedback.other}
            onChange={e => onStateChange({ feedback: { ...appState.feedback, other: e.target.value } })}
          />
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'settings':   return renderSettings();
      case 'responses':  return renderResponses();
      case 'files':      return renderFiles();
      case 'query_tab':  return renderQuery();
      case 'urls':       return renderUrls();
      case 'feedback':   return renderFeedback();
    }
  };

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

export default UtilityTabs;
