import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  percentage: number;
  currentTask?: string;
  currentPhase?: string;
  completedTasks?: number;
  totalTasks?: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  currentTask,
  currentPhase,
  completedTasks,
  totalTasks
}) => {
  return (
    <div className="progress-bar-container">
      <div className="progress-info">
        <div className="progress-text">
          {currentTask ? (
            <span className="current-task">
              <strong>{currentPhase ? `${currentPhase}: ` : ''}</strong>
              {currentTask}
            </span>
          ) : (
            <span className="current-task">Processando...</span>
          )}
        </div>
        <div className="progress-stats">
          <span className="percentage">{percentage.toFixed(0)}%</span>
          {completedTasks !== undefined && totalTasks !== undefined && (
            <span className="task-count">
              {completedTasks}/{totalTasks} tarefas
            </span>
          )}
        </div>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        >
          <div className="progress-shine"></div>
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
