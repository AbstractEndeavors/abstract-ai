import React from 'react';

interface OutputOptionsProps {
  onSubmit: () => void;
  onClearRequests: () => void;
  onClearChunks: () => void;
  onGenReadme: () => void;
  isSubmitting: boolean;
}

const OutputOptions: React.FC<OutputOptionsProps> = ({
  onSubmit,
  onClearRequests,
  onClearChunks,
  onGenReadme,
  isSubmitting,
}) => {
  return (
    <div className="output-options">
      <button
        onClick={onSubmit}
        disabled={isSubmitting}
        className="action-btn submit-btn"
      >
        {isSubmitting ? 'SUBMITTING...' : 'SUBMIT QUERY'}
      </button>
      <button onClick={onClearRequests} className="action-btn clear-btn">
        CLEAR REQUESTS
      </button>
      <button onClick={onClearChunks} className="action-btn clear-btn">
        CLEAR CHUNKS
      </button>
      <button onClick={onGenReadme} className="action-btn readme-btn">
        GEN README
      </button>
    </div>
  );
};

export default OutputOptions;
