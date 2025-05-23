// src/components/projects/CreateProjectModal.tsx (VERSÃO EM PORTUGUÊS)
import React, { useState } from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import './CreateProjectModal.css';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (projectData: ProjectFormData) => void;
}

export interface ProjectFormData {
  name: string;
  description: string;
  domain: string;
  startFrom: 'blank' | 'template';
  template?: string;
  defaultLLM: string;
  framework: string;
  memorySystem: string;
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ 
  isOpen, 
  onClose, 
  onCreateProject 
}) => {
  const { enterProjectContext } = useNavigation();
  
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    domain: '',
    startFrom: 'blank',
    defaultLLM: 'OpenAI GPT-4',
    framework: 'CrewAI',
    memorySystem: 'LangChain'
  });

  const [showTemplateSelect, setShowTemplateSelect] = useState(false);

  // Dados de exemplo para os selects
  const domains = ['Atendimento', 'Jurídico', 'Educação', 'Saúde', 'Finanças', 'Outro'];
  const templates = ['Assistente de Atendimento', 'Análise de Documentos', 'Pesquisa Acadêmica', 'Personalizado'];
  const llmOptions = ['OpenAI GPT-4', 'OpenAI GPT-3.5', 'Claude 3 Opus', 'Claude 3 Sonnet', 'Llama 3'];
  const frameworkOptions = ['CrewAI', 'LangChain', 'AutoGen', 'LlamaIndex'];
  const memoryOptions = ['LangChain', 'Redis', 'Pinecone', 'ChromaDB', 'Nenhum'];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleRadioChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value as 'blank' | 'template';
    setFormData(prev => ({ ...prev, startFrom: value }));
    setShowTemplateSelect(value === 'template');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 1. Gerar ID único para o projeto
    const projectId = `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 2. Criar o projeto (lógica original) - incluindo o ID gerado
    const projectWithId = {
      ...formData,
      id: projectId
    };
    onCreateProject(projectWithId);
    
    // 3. Entrar no contexto do projeto e mudar a sidebar (SEM navegar ainda)
    enterProjectContext(projectId, formData.name);
    
    // 4. Fechar o modal
    onClose();
    
    // 5. Limpar formulário para próxima vez
    setFormData({
      name: '',
      description: '',
      domain: '',
      startFrom: 'blank',
      defaultLLM: 'OpenAI GPT-4',
      framework: 'CrewAI',
      memorySystem: 'LangChain'
    });
    setShowTemplateSelect(false);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="create-project-modal">
        <div className="modal-header">
          <h2>CRIAR NOVO PROJETO</h2>
          <div className="modal-actions">
            <button className="close-button" onClick={onClose}>×</button>
            <button className="cancel-button" onClick={onClose}>Cancelar</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">NOME DO PROJETO:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Digite o nome do projeto"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">DESCRIÇÃO:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Descreva brevemente o objetivo do projeto"
              rows={3}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="domain">DOMÍNIO:</label>
            <select
              id="domain"
              name="domain"
              value={formData.domain}
              onChange={handleInputChange}
              required
            >
              <option value="" disabled>Selecione o domínio</option>
              {domains.map(domain => (
                <option key={domain} value={domain}>{domain}</option>
              ))}
            </select>
          </div>
          
          <div className="form-group start-from-group">
            <label>INICIAR A PARTIR DE:</label>
            <div className="radio-options">
              <div className="radio-option">
                <input
                  type="radio"
                  id="blank"
                  name="startFrom"
                  value="blank"
                  checked={formData.startFrom === 'blank'}
                  onChange={handleRadioChange}
                />
                <label htmlFor="blank">Projeto em Branco</label>
              </div>
              
              <div className="radio-option">
                <input
                  type="radio"
                  id="template"
                  name="startFrom"
                  value="template"
                  checked={formData.startFrom === 'template'}
                  onChange={handleRadioChange}
                />
                <label htmlFor="template">Modelo</label>
                
                {showTemplateSelect && (
                  <select
                    name="template"
                    value={formData.template || ''}
                    onChange={handleInputChange}
                    className="template-select"
                  >
                    <option value="" disabled>Selecione um modelo</option>
                    {templates.map(template => (
                      <option key={template} value={template}>{template}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>
          </div>
          
          <div className="advanced-options">
            <h3>OPÇÕES AVANÇADAS:</h3>
            <div className="advanced-options-content">
              <div className="advanced-option">
                <label htmlFor="defaultLLM">LLM Padrão:</label>
                <select
                  id="defaultLLM"
                  name="defaultLLM"
                  value={formData.defaultLLM}
                  onChange={handleInputChange}
                >
                  {llmOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              
              <div className="advanced-option">
                <label htmlFor="framework">Framework:</label>
                <select
                  id="framework"
                  name="framework"
                  value={formData.framework}
                  onChange={handleInputChange}
                >
                  {frameworkOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              
              <div className="advanced-option">
                <label htmlFor="memorySystem">Sistema de Memória:</label>
                <select
                  id="memorySystem"
                  name="memorySystem"
                  value={formData.memorySystem}
                  onChange={handleInputChange}
                >
                  {memoryOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          <div className="form-actions">
            <button type="button" className="back-button" onClick={onClose}>VOLTAR</button>
            <button type="submit" className="create-button">CRIAR ▶</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectModal;