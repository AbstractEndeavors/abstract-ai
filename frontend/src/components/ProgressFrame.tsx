import React from 'react';
import type { Progress } from '../types';

interface ProgressFrameProps {
  progress: Progress;
  title: string;
  onTitleChange: (title: string) => void;
  onNavPrev: () => void;
  onNavNext: () => void;
  queryIndex: number;
  queryTotal: number;
}

const ProgressFrame: React.FC<ProgressFrameProps> = ({
  progress,
  title,
  onTitleChange,
  onNavPrev,
  onNavNext,
  queryIndex,
  queryTotal,
}) => {
  return (
    <div className="progress-frame">
      <div className="progress-row">
        <input
          type="text"
          readOnly
          value={progress.status_text}
          className="status-input"
          placeholder="Status..."
        />
        <progress
          value={progress.percentage}
          max={100}
          className="progress-bar"
        />
        <span className="query-count">
          Queries: {progress.query_count}
        </span>
      </div>
      <div className="progress-row">
        <input
          type="text"
          value={title}
          onChange={e => onTitleChange(e.target.value)}
          className="title-input"
          placeholder="Title..."
        />
        <div className="response-nav">
          <button onClick={onNavPrev} disabled={queryIndex <= 0} className="nav-btn">&#8249; Prev</button>
          <span className="nav-label">
            Response: {queryTotal === 0 ? '0 / 0' : `${queryIndex + 1} / ${queryTotal}`}
          </span>
          <button onClick={onNavNext} disabled={queryIndex >= queryTotal - 1} className="nav-btn">Next &#8250;</button>
        </div>
      </div>
    </div>
  );
};

export default ProgressFrame;
