import React, { useState, useEffect, useCallback } from "react";
import "../documents/RequirementsHistoryModal.css"; // Reusa o CSS de modal de histórico

// Mesma base/token usados por petriNetService.ts (REACT_APP_API_URL)
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const getAuthHeaders = () => {
  const token =
    localStorage.getItem("accessToken") || localStorage.getItem("token") || "";
  return {
    Authorization: token ? `Bearer ${token}` : "",
    "Content-Type": "application/json",
  };
};

const formatDate = (dateString) => {
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

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const getTypeIcon = (type) => {
  const icons = {
    initial_generation: "🚀",
    ai_refinement: "✨",
    manual_edit: "📝",
  };
  return icons[type] || "📄";
};

const getTypeLabel = (type) => {
  const labels = {
    initial_generation: "Geração Inicial",
    ai_refinement: "Refinamento IA",
    manual_edit: "Edição Manual",
  };
  return labels[type] || type;
};

const getTypeBadge = (type) => {
  const typeColors = {
    initial_generation: "type-analysis",
    ai_refinement: "type-refinement",
    manual_edit: "type-manual",
  };
  return typeColors[type] || "type-manual";
};

const PetriNetHistoryModal = ({ isOpen, onClose, projectId, onRestored }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [restoringVersion, setRestoringVersion] = useState(null);

  const loadVersions = useCallback(async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE}/petri-net/${projectId}/versions`,
        {
          method: "GET",
          headers: getAuthHeaders(),
        }
      );
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
      console.error("Error loading petri-net versions:", err);
      setError("Erro ao carregar histórico de versões");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (isOpen) {
      loadVersions();
    }
  }, [isOpen, loadVersions]);

  const handleRestore = async (version) => {
    if (!projectId || restoringVersion !== null) return;
    setRestoringVersion(version);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE}/petri-net/${projectId}/restore/${version}`,
        {
          method: "POST",
          headers: getAuthHeaders(),
        }
      );
      if (response.status === 401 || response.status === 403) {
        setError("Sessão expirada. Faça login novamente.");
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      // Restauração persistida em project_data; recarrega o editor.
      if (onRestored) onRestored();
      onClose();
    } catch (err) {
      console.error("Error restoring petri-net version:", err);
      setError("Erro ao restaurar versão");
    } finally {
      setRestoringVersion(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="history-modal">
        <div className="modal-header">
          <h2>📜 Histórico de Versões — Rede de Petri</h2>
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
                As versões da Rede de Petri aparecerão aqui
              </p>
            </div>
          )}

          {!loading && !error && versions.length > 0 && (
            <div className="sessions-list">
              {versions.map((version) => (
                <div key={version.version} className="session-item">
                  <div className="session-header">
                    <div className="session-title">
                      <span className="session-icon">
                        {getTypeIcon(version.change_type)}
                      </span>
                      <span className="session-name">
                        v{version.version}
                        {version.is_approved_version ? " ✅ (aprovada)" : ""}
                      </span>
                    </div>
                    <span
                      className={`status-badge ${getTypeBadge(
                        version.change_type
                      )}`}
                    >
                      {getTypeLabel(version.change_type)}
                    </span>
                  </div>

                  <div className="session-details">
                    <div className="session-info">
                      <span className="info-label">Criado em:</span>
                      <span className="info-value">
                        {formatDate(version.created_at)}
                      </span>
                    </div>

                    <div className="session-info">
                      <span className="info-label">Descrição:</span>
                      <span className="info-value">
                        {version.change_description || "—"}
                      </span>
                    </div>

                    <div className="session-info">
                      <span className="info-label">Tamanho:</span>
                      <span className="info-value">
                        {formatFileSize(version.doc_size)}
                      </span>
                    </div>
                  </div>

                  <div className="session-action">
                    <button
                      className="btn-retry"
                      onClick={() => handleRestore(version.version)}
                      disabled={restoringVersion !== null}
                    >
                      {restoringVersion === version.version
                        ? "⏳ Restaurando..."
                        : "Restaurar esta versão"}
                    </button>
                  </div>
                </div>
              ))}
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

export default PetriNetHistoryModal;
