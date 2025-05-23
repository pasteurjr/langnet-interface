// src/components/agents/AgentSpecifierModal.tsx
import React, { useState } from 'react';
import './AgentSpecifierModal.css';

interface AgentSpecifierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSpecify: (agents: any[]) => void;
  projectId: string;
}

const AgentSpecifierModal: React.FC<AgentSpecifierModalProps> = ({
  isOpen,
  onClose,
  onSpecify,
  projectId
}) => {
  const [documents, setDocuments] = useState<File[]>([]);
  const [instructions, setInstructions] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setDocuments([...documents, ...newFiles]);
    }
  };

  const handleRemoveDocument = (index: number) => {
    setDocuments(documents.filter((_, i) => i !== index));
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const newFiles = Array.from(e.dataTransfer.files);
      setDocuments([...documents, ...newFiles]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleSpecify = async () => {
    if (documents.length === 0 && !instructions) {
      alert('Por favor, adicione documentos ou instruções');
      return;
    }

    setIsProcessing(true);

    // Simular processamento - aqui você faria a chamada real para o LLM
    setTimeout(() => {
      // Resultado simulado
      const specifiedAgents = [
        {
          name: 'customer_inquiry_agent',
          role: 'Agente especializado em receber e classificar consultas de clientes',
          goal: 'Identificar a natureza da consulta e direcionar para o agente apropriado',
          backstory: 'Experiente em atendimento inicial com habilidade para identificar rapidamente as necessidades dos clientes',
          tools: ['classification_tool', 'routing_tool', 'customer_database_tool'],
          verbose: true,
          allow_delegation: true
        },
        {
          name: 'billing_specialist_agent',
          role: 'Especialista em questões de faturamento e pagamentos',
          goal: 'Resolver problemas relacionados a cobranças, faturas e pagamentos',
          backstory: 'Profundo conhecimento em sistemas de billing e políticas de cobrança da empresa',
          tools: ['billing_system_tool', 'payment_processor_tool', 'invoice_generator_tool'],
          verbose: true,
          allow_delegation: false
        }
      ];

      onSpecify(specifiedAgents);
      setIsProcessing(false);
      
      // Limpar o modal
      setDocuments([]);
      setInstructions('');
    }, 3000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="agent-specifier-modal">
        <div className="modal-header">
          <h2>🤖 ESPECIFICADOR DE AGENTES</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="specifier-intro">
            <p>
              O Especificador de Agentes utiliza IA para analisar documentos e gerar 
              automaticamente definições de agentes baseadas nos requisitos identificados.
            </p>
          </div>

          <div className="form-section">
            <h3>📄 Documentos de Entrada</h3>
            
            <div 
              className="drop-zone"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <p>Arraste arquivos aqui ou clique para selecionar</p>
              <p className="file-types">Suportados: PDF, DOC, DOCX, TXT, MD</p>
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload" className="btn-upload">
                Selecionar Arquivos
              </label>
            </div>

            {documents.length > 0 && (
              <div className="uploaded-files">
                <h4>Arquivos carregados:</h4>
                {documents.map((file, index) => (
                  <div key={index} className="file-item">
                    <span className="file-icon">📄</span>
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                    <button 
                      className="btn-remove"
                      onClick={() => handleRemoveDocument(index)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="form-section">
            <h3>📝 Instruções Adicionais</h3>
            <textarea
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="Forneça instruções específicas sobre os tipos de agentes que deseja criar, domínio da aplicação, requisitos especiais, etc."
              rows={6}
            />
          </div>

          <div className="specifier-options">
            <h3>⚙️ Opções de Geração</h3>
            <div className="options-grid">
              <label>
                <input type="checkbox" defaultChecked />
                Incluir ferramentas sugeridas
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Gerar backstories detalhadas
              </label>
              <label>
                <input type="checkbox" />
                Criar agente supervisor
              </label>
              <label>
                <input type="checkbox" defaultChecked />
                Otimizar para colaboração
              </label>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose} disabled={isProcessing}>
            Cancelar
          </button>
          <button 
            className="btn-specify" 
            onClick={handleSpecify}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <span className="spinner"></span>
                Processando...
              </>
            ) : (
              '🚀 Especificar Agentes'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentSpecifierModal;