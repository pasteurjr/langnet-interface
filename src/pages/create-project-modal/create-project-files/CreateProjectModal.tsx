import React, { useState } from 'react';
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
    onCreateProject(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="create-project-modal">
        <div className="modal-header">
          <h2>CREATE NEW PROJECT</h2>
          <div className="modal-actions">
            <button className="close-button" onClick={onClose}>×</button>
            <button className="cancel-button" onClick={onClose}>Cancel</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">PROJECT NAME:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">DESCRIPTION:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={2}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="domain">DOMAIN:</label>
            <select
              id="domain"
              name="domain"
              value={formData.domain}
              onChange={handleInputChange}
            >
              <option value="" disabled>Select domain</option>
              {domains.map(domain => (
                <option key={domain} value={domain}>{domain}</option>
              ))}
            </select>
          </div>
          
          <div className="form-group start-from-group">
            <label>START FROM:</label>
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
                <label htmlFor="blank">Blank Project</label>
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
                <label htmlFor="template">Template</label>
                
                {showTemplateSelect && (
                  <select
                    name="template"
                    value={formData.template || ''}
                    onChange={handleInputChange}
                    className="template-select"
                  >
                    <option value="" disabled>Select template</option>
                    {templates.map(template => (
                      <option key={template} value={template}>{template}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>
          </div>
          
          <div className="advanced-options">
            <h3>ADVANCED OPTIONS:</h3>
            <div className="advanced-options-content">
              <div className="advanced-option">
                <label htmlFor="defaultLLM">Default LLM:</label>
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
                <label htmlFor="memorySystem">Memory System:</label>
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
            <button type="button" className="back-button" onClick={onClose}>BACK</button>
            <button type="submit" className="create-button">CREATE ▶</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectModal;
