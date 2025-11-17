import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RequirementsDocumentViewer } from '../components/documents/RequirementsDocumentViewer';

const RequirementsDocumentPage: React.FC = () => {
  const { projectId, executionId } = useParams<{ projectId: string; executionId: string }>();
  const navigate = useNavigate();

  const handleClose = () => {
    navigate(`/project/${projectId}/documents`);
  };

  if (!executionId || !projectId) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Missing Parameters</h2>
        <p>Project ID and Execution ID are required.</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  return (
    <RequirementsDocumentViewer
      executionId={executionId}
      projectId={projectId}
      onClose={handleClose}
    />
  );
};

export default RequirementsDocumentPage;
