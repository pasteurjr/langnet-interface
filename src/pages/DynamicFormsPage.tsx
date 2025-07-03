// src/pages/DynamicFormsPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import './DynamicFormsPage.css';

// Types based on requirements from docs
interface FormField {
  id: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'textarea' | 'checkbox' | 'radio' | 'file' | 'date' | 'email' | 'url';
  label: string;
  placeholder?: string;
  required: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  options?: Array<{ value: string; label: string }>;
  defaultValue?: any;
  description?: string;
  conditional?: {
    field: string;
    value: any;
    operator: 'equals' | 'not_equals' | 'contains' | 'greater' | 'less';
  };
}

interface FormTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  fields: FormField[];
  createdAt: string;
  isSystem: boolean;
}

interface FormInstance {
  id: string;
  templateId: string;
  name: string;
  data: Record<string, any>;
  status: 'draft' | 'completed' | 'submitted';
  createdAt: string;
  updatedAt: string;
}

interface ValidationResult {
  field: string;
  message: string;
  type: 'error' | 'warning';
}

const DynamicFormsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [templates, setTemplates] = useState<FormTemplate[]>([]);
  const [forms, setForms] = useState<FormInstance[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<FormTemplate | null>(null);
  const [activeForm, setActiveForm] = useState<FormInstance | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [validationErrors, setValidationErrors] = useState<ValidationResult[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isFormBuilder, setIsFormBuilder] = useState(false);
  const [newTemplate, setNewTemplate] = useState<Partial<FormTemplate>>({
    name: '',
    description: '',
    category: 'project',
    fields: []
  });

  // Mock data - seguindo padrão das outras páginas
  useEffect(() => {
    const mockTemplates: FormTemplate[] = [
      {
        id: '1',
        name: 'Configuração de Agente',
        description: 'Formulário para configurar novos agentes no projeto',
        category: 'agent',
        isSystem: true,
        createdAt: '2025-01-10T10:00:00Z',
        fields: [
          {
            id: 'name',
            type: 'text',
            label: 'Nome do Agente',
            placeholder: 'Ex: Customer Service Agent',
            required: true,
            validation: { min: 3, max: 50, message: 'Nome deve ter entre 3 e 50 caracteres' }
          },
          {
            id: 'role',
            type: 'select',
            label: 'Função',
            required: true,
            options: [
              { value: 'customer_service', label: 'Atendimento ao Cliente' },
              { value: 'data_analyst', label: 'Analista de Dados' },
              { value: 'content_creator', label: 'Criador de Conteúdo' },
              { value: 'quality_assurance', label: 'Controle de Qualidade' }
            ]
          },
          {
            id: 'goal',
            type: 'textarea',
            label: 'Objetivo Principal',
            placeholder: 'Descreva o objetivo principal deste agente...',
            required: true,
            validation: { min: 20, max: 500, message: 'Objetivo deve ter entre 20 e 500 caracteres' }
          },
          {
            id: 'tools',
            type: 'multiselect',
            label: 'Ferramentas Disponíveis',
            required: false,
            options: [
              { value: 'web_search', label: 'Busca na Web' },
              { value: 'file_read', label: 'Leitura de Arquivos' },
              { value: 'email_send', label: 'Envio de Email' },
              { value: 'database_query', label: 'Consulta ao Banco' }
            ]
          },
          {
            id: 'verbose',
            type: 'checkbox',
            label: 'Modo Verboso',
            required: false,
            defaultValue: false
          }
        ]
      },
      {
        id: '2',
        name: 'Avaliação de Qualidade',
        description: 'Formulário para avaliar a qualidade dos resultados',
        category: 'evaluation',
        isSystem: false,
        createdAt: '2025-01-12T14:30:00Z',
        fields: [
          {
            id: 'task_id',
            type: 'text',
            label: 'ID da Tarefa',
            required: true
          },
          {
            id: 'rating',
            type: 'radio',
            label: 'Avaliação Geral',
            required: true,
            options: [
              { value: '1', label: '⭐ Muito Ruim' },
              { value: '2', label: '⭐⭐ Ruim' },
              { value: '3', label: '⭐⭐⭐ Regular' },
              { value: '4', label: '⭐⭐⭐⭐ Bom' },
              { value: '5', label: '⭐⭐⭐⭐⭐ Excelente' }
            ]
          },
          {
            id: 'feedback',
            type: 'textarea',
            label: 'Comentários',
            placeholder: 'Adicione seus comentários sobre a execução...',
            required: false
          },
          {
            id: 'follow_up',
            type: 'checkbox',
            label: 'Requer acompanhamento',
            required: false,
            defaultValue: false
          },
          {
            id: 'follow_up_date',
            type: 'date',
            label: 'Data para acompanhamento',
            required: false,
            conditional: {
              field: 'follow_up',
              value: true,
              operator: 'equals'
            }
          }
        ]
      },
      {
        id: '3',
        name: 'Configuração de Projeto',
        description: 'Formulário wizard para configuração inicial de projetos',
        category: 'project',
        isSystem: true,
        createdAt: '2025-01-15T09:15:00Z',
        fields: [
          {
            id: 'project_name',
            type: 'text',
            label: 'Nome do Projeto',
            required: true,
            validation: { min: 3, max: 100 }
          },
          {
            id: 'domain',
            type: 'select',
            label: 'Domínio',
            required: true,
            options: [
              { value: 'ecommerce', label: 'E-commerce' },
              { value: 'healthcare', label: 'Saúde' },
              { value: 'finance', label: 'Financeiro' },
              { value: 'education', label: 'Educação' },
              { value: 'manufacturing', label: 'Manufatura' }
            ]
          },
          {
            id: 'complexity',
            type: 'radio',
            label: 'Complexidade',
            required: true,
            options: [
              { value: 'simple', label: 'Simples (1-3 agentes)' },
              { value: 'medium', label: 'Médio (4-8 agentes)' },
              { value: 'complex', label: 'Complexo (9+ agentes)' }
            ]
          },
          {
            id: 'budget',
            type: 'number',
            label: 'Orçamento (USD)',
            required: false,
            validation: { min: 0, max: 1000000 }
          }
        ]
      }
    ];

    const mockForms: FormInstance[] = [
      {
        id: '1',
        templateId: '1',
        name: 'Agente Atendimento V1',
        status: 'completed',
        createdAt: '2025-01-16T10:30:00Z',
        updatedAt: '2025-01-16T11:00:00Z',
        data: {
          name: 'Customer Service Agent',
          role: 'customer_service',
          goal: 'Fornecer atendimento ao cliente de alta qualidade, resolvendo dúvidas e problemas de forma eficiente e empática.',
          tools: ['web_search', 'database_query'],
          verbose: true
        }
      },
      {
        id: '2',
        templateId: '2',
        name: 'Avaliação Task #123',
        status: 'draft',
        createdAt: '2025-01-16T15:20:00Z',
        updatedAt: '2025-01-16T15:25:00Z',
        data: {
          task_id: 'TASK-123',
          rating: '4'
        }
      }
    ];

    setTemplates(mockTemplates);
    setForms(mockForms);
  }, [projectId]);

  const validateField = (field: FormField, value: any): ValidationResult | null => {
    if (field.required && (!value || value === '')) {
      return {
        field: field.id,
        message: `${field.label} é obrigatório`,
        type: 'error'
      };
    }

    if (field.validation && value) {
      const { min, max, pattern, message } = field.validation;
      
      if (field.type === 'text' || field.type === 'textarea') {
        if (min && value.length < min) {
          return {
            field: field.id,
            message: message || `${field.label} deve ter pelo menos ${min} caracteres`,
            type: 'error'
          };
        }
        if (max && value.length > max) {
          return {
            field: field.id,
            message: message || `${field.label} deve ter no máximo ${max} caracteres`,
            type: 'error'
          };
        }
      }

      if (field.type === 'number') {
        const numValue = Number(value);
        if (min && numValue < min) {
          return {
            field: field.id,
            message: message || `${field.label} deve ser pelo menos ${min}`,
            type: 'error'
          };
        }
        if (max && numValue > max) {
          return {
            field: field.id,
            message: message || `${field.label} deve ser no máximo ${max}`,
            type: 'error'
          };
        }
      }

      if (pattern && !new RegExp(pattern).test(value)) {
        return {
          field: field.id,
          message: message || `${field.label} tem formato inválido`,
          type: 'error'
        };
      }
    }

    return null;
  };

  const validateForm = (template: FormTemplate, data: Record<string, any>): ValidationResult[] => {
    const errors: ValidationResult[] = [];
    
    template.fields.forEach(field => {
      // Check conditional fields
      if (field.conditional) {
        const conditionField = template.fields.find(f => f.id === field.conditional!.field);
        const conditionValue = data[field.conditional.field];
        const shouldShow = field.conditional.operator === 'equals' 
          ? conditionValue === field.conditional.value
          : conditionValue !== field.conditional.value;
        
        if (!shouldShow) return;
      }

      const error = validateField(field, data[field.id]);
      if (error) errors.push(error);
    });

    return errors;
  };

  const handleFieldChange = (fieldId: string, value: any) => {
    const newData = { ...formData, [fieldId]: value };
    setFormData(newData);

    // Real-time validation
    if (selectedTemplate) {
      const errors = validateForm(selectedTemplate, newData);
      setValidationErrors(errors);
    }
  };

  const handleFormSubmit = () => {
    if (!selectedTemplate) return;

    const errors = validateForm(selectedTemplate, formData);
    setValidationErrors(errors);

    if (errors.length === 0) {
      const newForm: FormInstance = {
        id: `form-${Date.now()}`,
        templateId: selectedTemplate.id,
        name: `${selectedTemplate.name} - ${new Date().toLocaleDateString()}`,
        status: 'completed',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        data: formData
      };

      setForms([...forms, newForm]);
      setFormData({});
      setSelectedTemplate(null);
      alert('Formulário enviado com sucesso!');
    }
  };

  const shouldShowField = (field: FormField): boolean => {
    if (!field.conditional) return true;
    
    const conditionValue = formData[field.conditional.field];
    return field.conditional.operator === 'equals' 
      ? conditionValue === field.conditional.value
      : conditionValue !== field.conditional.value;
  };

  const renderField = (field: FormField) => {
    if (!shouldShowField(field)) return null;

    const error = validationErrors.find(e => e.field === field.id);
    const fieldClass = `form-field ${error ? 'has-error' : ''}`;

    switch (field.type) {
      case 'text':
      case 'email':
      case 'url':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            {field.description && (
              <div className="field-description">{field.description}</div>
            )}
            <input
              type={field.type}
              placeholder={field.placeholder}
              value={formData[field.id] || ''}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              className="form-input"
            />
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'number':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="number"
              placeholder={field.placeholder}
              value={formData[field.id] || ''}
              onChange={(e) => handleFieldChange(field.id, Number(e.target.value))}
              min={field.validation?.min}
              max={field.validation?.max}
              className="form-input"
            />
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'textarea':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <textarea
              placeholder={field.placeholder}
              value={formData[field.id] || ''}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              className="form-textarea"
              rows={4}
            />
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'select':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <select
              value={formData[field.id] || ''}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              className="form-select"
            >
              <option value="">Selecione uma opção</option>
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'multiselect':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <div className="checkbox-group">
              {field.options?.map(option => (
                <label key={option.value} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={(formData[field.id] || []).includes(option.value)}
                    onChange={(e) => {
                      const currentValues = formData[field.id] || [];
                      const newValues = e.target.checked
                        ? [...currentValues, option.value]
                        : currentValues.filter((v: string) => v !== option.value);
                      handleFieldChange(field.id, newValues);
                    }}
                  />
                  {option.label}
                </label>
              ))}
            </div>
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'radio':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <div className="radio-group">
              {field.options?.map(option => (
                <label key={option.value} className="radio-item">
                  <input
                    type="radio"
                    name={field.id}
                    value={option.value}
                    checked={formData[field.id] === option.value}
                    onChange={(e) => handleFieldChange(field.id, e.target.value)}
                  />
                  {option.label}
                </label>
              ))}
            </div>
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'checkbox':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="checkbox-item">
              <input
                type="checkbox"
                checked={formData[field.id] || field.defaultValue || false}
                onChange={(e) => handleFieldChange(field.id, e.target.checked)}
              />
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      case 'date':
        return (
          <div key={field.id} className={fieldClass}>
            <label className="field-label">
              {field.label}
              {field.required && <span className="required">*</span>}
            </label>
            <input
              type="date"
              value={formData[field.id] || ''}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              className="form-input"
            />
            {error && <div className="field-error">{error.message}</div>}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dynamic-forms-page">
      <div className="page-header">
        <div className="header-main">
          <h1>📝 Formulários Dinâmicos</h1>
          <p>Crie e gerencie formulários configuráveis para o projeto</p>
        </div>
        <div className="header-actions">
          <button
            className={`btn ${isFormBuilder ? 'btn-secondary' : 'btn-primary'}`}
            onClick={() => setIsFormBuilder(!isFormBuilder)}
          >
            {isFormBuilder ? '📋 Ver Formulários' : '🛠️ Criar Template'}
          </button>
        </div>
      </div>

      <div className="page-content">
        {!selectedTemplate && !isFormBuilder ? (
          // Templates List
          <div className="templates-section">
            <div className="section-header">
              <h2>Templates Disponíveis</h2>
              <p>Selecione um template para preencher um formulário</p>
            </div>
            
            <div className="templates-grid">
              {templates.map(template => (
                <div 
                  key={template.id} 
                  className="template-card"
                  onClick={() => setSelectedTemplate(template)}
                >
                  <div className="template-header">
                    <h3>{template.name}</h3>
                    <span className={`template-badge ${template.isSystem ? 'system' : 'custom'}`}>
                      {template.isSystem ? 'Sistema' : 'Customizado'}
                    </span>
                  </div>
                  <p className="template-description">{template.description}</p>
                  <div className="template-meta">
                    <span className="template-category">{template.category}</span>
                    <span className="template-fields">{template.fields.length} campos</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Forms History */}
            <div className="forms-history">
              <h2>Histórico de Formulários</h2>
              <div className="forms-list">
                {forms.map(form => (
                  <div key={form.id} className="form-card">
                    <div className="form-header">
                      <h4>{form.name}</h4>
                      <span className={`form-status ${form.status}`}>
                        {form.status}
                      </span>
                    </div>
                    <div className="form-meta">
                      <span>Template: {templates.find(t => t.id === form.templateId)?.name}</span>
                      <span>Criado: {new Date(form.createdAt).toLocaleDateString('pt-BR')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : selectedTemplate ? (
          // Form Filling
          <div className="form-container">
            <div className="form-header">
              <button 
                className="back-btn"
                onClick={() => {
                  setSelectedTemplate(null);
                  setFormData({});
                  setValidationErrors([]);
                }}
              >
                ← Voltar
              </button>
              <div>
                <h2>{selectedTemplate.name}</h2>
                <p>{selectedTemplate.description}</p>
              </div>
            </div>

            <div className="form-content">
              <div className="form-fields">
                {selectedTemplate.fields.map(renderField)}
              </div>

              <div className="form-actions">
                <button 
                  className="btn btn-secondary"
                  onClick={() => {
                    setSelectedTemplate(null);
                    setFormData({});
                    setValidationErrors([]);
                  }}
                >
                  Cancelar
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={handleFormSubmit}
                  disabled={validationErrors.length > 0}
                >
                  Enviar Formulário
                </button>
              </div>

              {validationErrors.length > 0 && (
                <div className="validation-summary">
                  <h4>⚠️ Erros de validação:</h4>
                  <ul>
                    {validationErrors.map(error => (
                      <li key={error.field}>{error.message}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          // Form Builder (placeholder)
          <div className="form-builder">
            <div className="builder-header">
              <h2>🛠️ Construtor de Templates</h2>
              <p>Funcionalidade em desenvolvimento</p>
            </div>
            <div className="builder-placeholder">
              <div className="placeholder-icon">🚧</div>
              <h3>Em Construção</h3>
              <p>O construtor visual de formulários será implementado em breve.</p>
              <button 
                className="btn btn-primary"
                onClick={() => setIsFormBuilder(false)}
              >
                Voltar aos Templates
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DynamicFormsPage;