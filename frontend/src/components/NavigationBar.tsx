import React from 'react';

interface NavigationBarProps {
  label: string;
  current: number;
  total: number;
  onPrev: () => void;
  onNext: () => void;
}

const NavigationBar: React.FC<NavigationBarProps> = ({ label, current, total, onPrev, onNext }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '4px 0' }}>
      <button onClick={onPrev} disabled={current <= 0} className="nav-btn">&#8249;</button>
      <span style={{ fontSize: '12px', color: '#aaa', minWidth: '100px' }}>
        {label}: {total === 0 ? '0 / 0' : `${current + 1} / ${total}`}
      </span>
      <button onClick={onNext} disabled={current >= total - 1} className="nav-btn">&#8250;</button>
    </div>
  );
};

export default NavigationBar;
