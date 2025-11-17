// src/components/projects/CreateProjectModal.tsx (VERSÃO EM PORTUGUÊS + API Integration)
import React, { useState, useEffect } from 'react';
import { useNavigation } from '../../contexts/NavigationContext';
import { toast } from 'react-toastify';
import { createProject, updateProject } from '../../services/projectService';
import { getCurrentUser } from '../../services/authService';
import './CreateProjectModal.css';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (projectData: ProjectFormData) => void;
  editMode?: boolean;
  initialData?: ProjectFormData;
}

export interface ProjectFormData {
  id?: string;
  name: string;
  description: string;
  domain: string;
  startFrom: 'blank' | 'template';
  template?: string;
  defaultLLM: string;
  framework: string;
  memorySystem: string;
  status?: string;
}

const defaultFormData: ProjectFormData = {
  name: '',
  description: '',
  domain: '',
  startFrom: 'blank',
  defaultLLM: 'OpenAI GPT-4',
  framework: 'CrewAI',
  memorySystem: 'LangChain'
};

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onCreateProject,
  editMode = false,
  initialData
}) => {
  const { enterProjectContext } = useNavigation();

  const [formData, setFormData] = useState<ProjectFormData>(defaultFormData);

  // Update form when initialData changes
  useEffect(() => {
    if (editMode && initialData) {
      setFormData(initialData);
    } else {
      setFormData(defaultFormData);
    }
  }, [editMode, initialData, isOpen]);

  const [showTemplateSelect, setShowTemplateSelect] = useState(false);
  const [loading, setLoading] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const currentUser = await getCurrentUser();
    if (!currentUser) {
      toast.error('Usuário não autenticado');
      return;
    }

    if (!formData.name || !formData.domain) {
      toast.error('Nome e domínio são obrigatórios');
      return;
    }

    setLoading(true);

    try {
      if (editMode && formData.id) {
        // Update existing project
        const updateData = {
          name: formData.name,
          description: formData.description || null,
          domain: formData.domain || null,
          framework: formData.framework.toLowerCase().replace(' ', '') as any,
          default_llm: formData.defaultLLM || null,
          memory_system: formData.memorySystem || null,
          start_from: formData.startFrom,
          template: formData.template || null,
          status: formData.status || 'draft'
        };

        await updateProject(formData.id, updateData);
        toast.success('Projeto atualizado com sucesso!');

        // Call parent callback
        onCreateProject({ ...formData });
      } else {
        // Create new project
        const apiData = {
          user_id: currentUser.id,
          name: formData.name,
          description: formData.description || null,
          domain: formData.domain || null,
          framework: formData.framework.toLowerCase().replace(' ', '') as any,
          default_llm: formData.defaultLLM || null,
          memory_system: formData.memorySystem || null,
          start_from: formData.startFrom,
          template: formData.template || null,
          status: 'draft'
        };

        const createdProject = await createProject(apiData);
        toast.success('Projeto criado com sucesso!');

        // Call parent callback
        onCreateProject({ ...formData, id: createdProject.id });

        // Enter project context
        enterProjectContext(createdProject.id, createdProject.name);
      }

      // Close modal
      onClose();

      // Reset form
      setFormData(defaultFormData);
      setShowTemplateSelect(false);
    } catch (error: any) {
      console.error('Error saving project:', error);
      toast.error(error.response?.data?.detail || `Erro ao ${editMode ? 'atualizar' : 'criar'} projeto`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="create-project-modal">
        <div className="modal-header">
          <h2>{editMode ? 'Editar Projeto' : 'Criar Novo Projeto'}</h2>
          <button className="close-button" onClick={onClose} title="Fechar">×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Nome do Projeto:</label>
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
            <label htmlFor="domain">Domínio:</label>
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

          <div className="form-group full-width">
            <label htmlFor="description">Descrição:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Descreva brevemente o objetivo do projeto"
              rows={2}
            />
          </div>

          <div className="form-group full-width start-from-group">
            <label>Iniciar a partir de:</label>
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
            <h3>Opções Avançadas:</h3>
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
            <button type="button" className="cancel-button-action" onClick={onClose} disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? (editMode ? 'Salvando...' : 'Criando...') : (editMode ? 'Salvar Alterações' : 'Criar Projeto')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateProjectModal;