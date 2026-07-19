import React, { useState, useEffect, useCallback } from "react";
import "../documents/RequirementsHistoryModal.css"; // Reusa o CSS de modal de histórico

const API_BASE = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api";

interface TestCaseVersion {
  version: number;
  created_at: string;
  change_description: string;
  change_type: "initial_generation" | "ai_refinement" | "manual_edit" | string;
  doc_size: number;
}

interface TestCaseHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string | null;
  currentVersion?: number;
  onSelectVersion: (version: number) => void;
}

const getAuthHeaders = (): HeadersInit => {
  const token =
    localStorage.getItem("accessToken") || localStorage.getItem("access_token") || "";
  return {
    Authorization: token ? `Bearer ${token}` : "",
    "Content-Type": "application/json",
  };
};

const formatDate = (dateString: string) => {
  if (!dateString) return "—";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString;
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatFileSize = (bytes: number) => {
  if (!bytes || bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const getTypeIcon = (type: string) => {
  const icons: { [key: string]: string } = {
    initial_generation: "🚀",
    ai_refinement: "✨",
    manual_edit: "📝",
  };
  return icons[type] || "📄";
};

const getTypeLabel = (type: string) => {
  const labels: { [key: string]: string } = {
    initial_generation: "Geração Inicial",
    ai_refinement: "Refinamento IA",
    manual_edit: "Edição Manual",
  };
  return labels[type] || type;
};

const getTypeBadge = (type: string) => {
  const typeColors: { [key: string]: string } = {
    initial_generation: "type-analysis",
    ai_refinement: "type-refinement",
    manual_edit: "type-manual",
  };
  return typeColors[type] || "type-manual";
};

const TestCaseHistoryModal: React.FC<TestCaseHistoryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  currentVersion,
  onSelectVersion,
}) => {
  const [versions, setVersions] = useState<TestCaseVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadVersions = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/test-cases/${sessionId}/versions`, {
        method: "GET",
        headers: getAuthHeaders(),
      });
      if (response.status === 401 || response.status === 403) {
        setError("Sessão expirada. Faça login novamente.");
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      setVersions(data.versions || []);
    } catch (err) {
      console.error("Error loading test-case versions:", err);
      setError("Erro ao carregar histórico de versões");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (isOpen) {
      loadVersions();
    }
  }, [isOpen, loadVersions]);

  const handleVersionClick = (version: number) => {
    onSelectVersion(version);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>📜 Histórico de Versões — Casos de Teste</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner-large"></div>
              <p>Carregando versões...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button className="btn-retry" onClick={loadVersions}>
                Tentar Novamente
              </button>
            </div>
          )}

          {!loading && !error && versions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>Nenhuma versão encontrada</p>
              <p className="empty-hint">
                As versões dos casos de teste aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && versions.length > 0 && (
            <div className="sessions-list">
              {versions.map((version) => {
                const isCurrent = currentVersion === version.version;
                return (
                  <div
                    key={version.version}
                    className="session-item"
                    onClick={() => handleVersionClick(version.version)}
                  >
                    <div className="session-header">
                      <div className="session-title">
                        <span className="session-icon">
                          {getTypeIcon(version.change_type)}
                        </span>
                        <span className="session-name">
                          v{version.version}
                          {isCurrent ? " (atual)" : ""}
                        </span>
                      </div>
                      <span className={`status-badge ${getTypeBadge(version.change_type)}`}>
                        {getTypeLabel(version.change_type)}
                      </span>
                    </div>

                    <div className="session-details">
                      <div className="session-info">
                        <span className="info-label">Criado em:</span>
                        <span className="info-value">{formatDate(version.created_at)}</span>
                      </div>

                      <div className="session-info">
                        <span className="info-label">Descrição:</span>
                        <span className="info-value">
                          {version.change_description || "—"}
                        </span>
                      </div>

                      <div className="session-info">
                        <span className="info-label">Tamanho do documento:</span>
                        <span className="info-value">{formatFileSize(version.doc_size)}</span>
                      </div>
                    </div>

                    <div className="session-action">
                      <span className="action-hint">Clique para visualizar →</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            {!loading && versions.length > 0 && (
              <span className="sessions-count">
                {versions.length} versão(ões) encontrada(s)
              </span>
            )}
          </div>
          <div className="footer-actions">
            <button className="btn-close" onClick={onClose}>
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestCaseHistoryModal;
