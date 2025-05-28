/* src/components/code/CodeGenerationModal.tsx */
import React, { useState } from 'react';
import { 
  CodeGenerationRequest,
  FrameworkType,
  MemorySystemType,
  LLMProviderType,
  PythonVersionType,
  DeploymentTargetType
} from '../../types/codeGeneration';
import './CodeGenerationModal.css';

interface CodeGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (request: CodeGenerationRequest) => void;
  projectId: string;
  isGenerating?: boolean;
}

const CodeGenerationModal: React.FC<CodeGenerationModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  projectId,
  isGenerating = false
}) => {
  const [framework, setFramework] = useState<FrameworkType>(FrameworkType.CREWAI);
  const [memorySystem, setMemorySystem] = useState<MemorySystemType>(MemorySystemType.LANGCHAIN_FULL);
  const [llmProvider, setLLMProvider] = useState<LLMProviderType>(LLMProviderType.OPENAI);
  const [pythonVersion, setPythonVersion] = useState<PythonVersionType>(PythonVersionType.PYTHON_311);
  const [deploymentTarget, setDeploymentTarget] = useState<DeploymentTargetType>(DeploymentTargetType.DOCKER);
  const [includeTests, setIncludeTests] = useState(true);
  const [includeDocumentation, setIncludeDocumentation] = useState(true);
  const [includeLangfuseIntegration, setIncludeLangfuseIntegration] = useState(true);
  const [includeDocker, setIncludeDocker] = useState(true);
  const [includeKubernetes, setIncludeKubernetes] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');
  const [outputStructure, setOutputStructure] = useState<'package' | 'single_file' | 'microservices'>('package');

  const handleGenerate = () => {
    const request: CodeGenerationRequest = {
      projectId,
      petriNetId: 'petri_1', // This should come from context
      agentIds: ['agent1', 'agent2'], // This should come from context
      taskIds: ['task1', 'task2'], // This should come from context
      framework,
      memorySystem,
      llmProvider,
      pythonVersion,
      includeTests,
      includeDocumentation,
      includeLangfuseIntegration,
      buildConfig: {
        pythonVersion,
        packageManager: 'pip',
        virtualEnvironment: true,
        requirements: [],
        devRequirements: [],
        buildTools: [],
        linting: {
          enabled: true,
          tools: ['flake8', 'black', 'isort'],
          configFiles: {}
        },
        formatting: {
          enabled: true,
          lineLength: 88,
          indentSize: 4,
          quotes: 'double'
        }
      },
      deploymentConfig: {
        target: deploymentTarget,
        environmentVariables: {},
        secrets: {},
        healthChecks: [],
        scaling: {
          enabled: false,
          minReplicas: 1,
          maxReplicas: 3,
          targetCPU: 80,
          targetMemory: 80,
          scaleUpDelay: 300,
          scaleDownDelay: 600
        }
      },
      testConfig: {
        generateTests: includeTests,
        testFramework: 'pytest',
        coverageThreshold: 80,
        integrationTests: true,
        performanceTests: false,
        mockExternalServices: true,
        testDataGeneration: true
      },
      monitoringConfig: {
        langfuseEnabled: includeLangfuseIntegration,
        customMetrics: [],
        alerting: {
          enabled: false,
          channels: [],
          rules: []
        }
      },
      customInstructions: customInstructions.trim() || undefined,
      outputStructure
    };
    
    onGenerate(request);
  };

  const getFrameworkInfo = (type: FrameworkType) => {
    switch (type) {
      case FrameworkType.CREWAI:
        return {
          icon: '🚢',
          title: 'CrewAI',
          description: 'Framework moderno para agentes colaborativos'
        };
      case FrameworkType.LANGCHAIN:
        return {
          icon: '🔗',
          title: 'LangChain',
          description: 'Framework completo para aplicações LLM'
        };
      case FrameworkType.AUTOGEN:
        return {
          icon: '🤖',
          title: 'AutoGen',
          description: 'Framework da Microsoft para agentes conversacionais'
        };
      case FrameworkType.CUSTOM:
        return {
          icon: '🛠️',
          title: 'Personalizado',
          description: 'Implementação customizada de agentes'
        };
    }
  };

  const getLLMProviderInfo = (type: LLMProviderType) => {
    switch (type) {
      case LLMProviderType.OPENAI:
        return {
          icon: '🤖',
          title: 'OpenAI',
          description: 'GPT-4, GPT-3.5 e modelos da OpenAI'
        };
      case LLMProviderType.ANTHROPIC:
        return {
          icon: '🧠',
          title: 'Anthropic',
          description: 'Claude 3 e modelos da Anthropic'
        };
      case LLMProviderType.AZURE_OPENAI:
        return {
          icon: '☁️',
          title: 'Azure OpenAI',
          description: 'OpenAI via Microsoft Azure'
        };
      case LLMProviderType.OLLAMA:
        return {
          icon: '🦙',
          title: 'Ollama',
          description: 'Modelos locais via Ollama'
        };
      default:
        return {
          icon: '🔧',
          title: 'Outro',
          description: 'Provedor personalizado'
        };
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="code-generation-modal">
        <div className="modal-header">
          <h2>🚀 Gerar Código Python</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="generation-step">
            <h3>🛠️ Framework e Tecnologias</h3>
            <p>Selecione o framework principal e tecnologias para seu sistema:</p>
            
            <div className="framework-grid">
              {Object.values(FrameworkType).map(frameworkType => {
                const info = getFrameworkInfo(frameworkType);
                return (
                  <div
                    key={frameworkType}
                    className={`framework-card ${framework === frameworkType ? 'selected' : ''}`}
                    onClick={() => setFramework(frameworkType)}
                  >
                    <div className="framework-icon">{info.icon}</div>
                    <div className="framework-info">
                      <div className="framework-title">{info.title}</div>
                      <div className="framework-description">{info.description}</div>
                    </div>
                    <div className="framework-radio">
                      <input
                        type="radio"
                        name="framework"
                        checked={framework === frameworkType}
                        onChange={() => setFramework(frameworkType)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="generation-step">
            <h3>🤖 Provedor de LLM</h3>
            <p>Escolha o provedor de modelo de linguagem:</p>
            
            <div className="llm-provider-grid">
              {Object.values(LLMProviderType).map(providerType => {
                const info = getLLMProviderInfo(providerType);
                return (
                  <div
                    key={providerType}
                    className={`provider-card ${llmProvider === providerType ? 'selected' : ''}`}
                    onClick={() => setLLMProvider(providerType)}
                  >
                    <div className="provider-icon">{info.icon}</div>
                    <div className="provider-info">
                      <div className="provider-title">{info.title}</div>
                      <div className="provider-description">{info.description}</div>
                    </div>
                    <div className="provider-radio">
                      <input
                        type="radio"
                        name="llmProvider"
                        checked={llmProvider === providerType}
                        onChange={() => setLLMProvider(providerType)}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="generation-step">
            <h3>⚙️ Configurações Técnicas</h3>
            <div className="config-grid">
              <div className="config-group">
                <h4>Ambiente Python</h4>
                <select
                  value={pythonVersion}
                  onChange={(e) => setPythonVersion(e.target.value as PythonVersionType)}
                  className="config-select"
                >
                  <option value={PythonVersionType.PYTHON_39}>Python 3.9</option>
                  <option value={PythonVersionType.PYTHON_310}>Python 3.10</option>
                  <option value={PythonVersionType.PYTHON_311}>Python 3.11</option>
                  <option value={PythonVersionType.PYTHON_312}>Python 3.12</option>
                </select>
              </div>

              <div className="config-group">
                <h4>Sistema de Memória</h4>
                <select
                  value={memorySystem}
                  onChange={(e) => setMemorySystem(e.target.value as MemorySystemType)}
                  className="config-select"
                >
                  <option value={MemorySystemType.LANGCHAIN_FULL}>LangChain Completo</option>
                  <option value={MemorySystemType.LANGCHAIN_SIMPLE}>LangChain Simples</option>
                  <option value={MemorySystemType.REDIS}>Redis</option>
                  <option value={MemorySystemType.POSTGRESQL}>PostgreSQL</option>
                  <option value={MemorySystemType.INMEMORY}>Em Memória</option>
                </select>
              </div>

              <div className="config-group">
                <h4>Target de Deploy</h4>
                <select
                  value={deploymentTarget}
                  onChange={(e) => setDeploymentTarget(e.target.value as DeploymentTargetType)}
                  className="config-select"
                >
                  <option value={DeploymentTargetType.LOCAL}>Local</option>
                  <option value={DeploymentTargetType.DOCKER}>Docker</option>
                  <option value={DeploymentTargetType.KUBERNETES}>Kubernetes</option>
                  <option value={DeploymentTargetType.AWS}>AWS</option>
                  <option value={DeploymentTargetType.AZURE}>Azure</option>
                  <option value={DeploymentTargetType.GCP}>Google Cloud</option>
                </select>
              </div>

              <div className="config-group">
                <h4>Estrutura de Saída</h4>
                <select
                  value={outputStructure}
                  onChange={(e) => setOutputStructure(e.target.value as any)}
                  className="config-select"
                >
                  <option value="package">Pacote Python</option>
                  <option value="single_file">Arquivo Único</option>
                  <option value="microservices">Microserviços</option>
                </select>
              </div>
            </div>
          </div>

          <div className="generation-step">
            <h3>📦 Componentes Inclusos</h3>
            <p>Selecione os componentes adicionais para incluir:</p>
            
            <div className="components-grid">
              <label className="component-option">
                <input
                  type="checkbox"
                  checked={includeTests}
                  onChange={(e) => setIncludeTests(e.target.checked)}
                />
                <div className="component-info">
                  <span className="component-icon">🧪</span>
                  <div>
                    <div className="component-title">Testes Automatizados</div>
                    <div className="component-description">Pytest com cobertura e testes de integração</div>
                  </div>
                </div>
              </label>

              <label className="component-option">
                <input
                  type="checkbox"
                  checked={includeDocumentation}
                  onChange={(e) => setIncludeDocumentation(e.target.checked)}
                />
                <div className="component-info">
                  <span className="component-icon">📚</span>
                  <div>
                    <div className="component-title">Documentação</div>
                    <div className="component-description">README, API docs e guias de uso</div>
                  </div>
                </div>
              </label>

              <label className="component-option">
                <input
                  type="checkbox"
                  checked={includeLangfuseIntegration}
                  onChange={(e) => setIncludeLangfuseIntegration(e.target.checked)}
                />
                <div className="component-info">
                  <span className="component-icon">📊</span>
                  <div>
                    <div className="component-title">Integração Langfuse</div>
                    <div className="component-description">Monitoramento e observabilidade LLM</div>
                  </div>
                </div>
              </label>

              <label className="component-option">
                <input
                  type="checkbox"
                  checked={includeDocker}
                  onChange={(e) => setIncludeDocker(e.target.checked)}
                />
                <div className="component-info">
                  <span className="component-icon">🐳</span>
                  <div>
                    <div className="component-title">Containerização</div>
                    <div className="component-description">Dockerfile e docker-compose</div>
                  </div>
                </div>
              </label>

              <label className="component-option">
                <input
                  type="checkbox"
                  checked={includeKubernetes}
                  onChange={(e) => setIncludeKubernetes(e.target.checked)}
                />
                <div className="component-info">
                  <span className="component-icon">☸️</span>
                  <div>
                    <div className="component-title">Kubernetes</div>
                    <div className="component-description">Manifests para deploy em K8s</div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div className="generation-step">
            <h3>📝 Instruções Personalizadas</h3>
            <p>Adicione instruções específicas para personalizar a geração de código:</p>
            <textarea
              className="instructions-textarea"
              placeholder="Ex: Adicionar middleware de autenticação JWT, usar padrão Repository para dados, incluir rate limiting, implementar cache Redis, etc."
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              rows={4}
            />
            <div className="instructions-help">
              <p>💡 Exemplos de instruções úteis:</p>
              <ul>
                <li>Padrões de arquitetura específicos (Repository, Factory, Observer)</li>
                <li>Middlewares e interceptadores (autenticação, logging, rate limiting)</li>
                <li>Configurações de performance (cache, pooling, async/await)</li>
                <li>Integração com APIs externas específicas</li>
                <li>Estruturas de dados e validações customizadas</li>
                <li>Configurações de segurança e compliance</li>
              </ul>
            </div>
          </div>

          <div className="generation-summary">
            <h3>📋 Resumo da Geração</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Framework:</span>
                <span className="summary-value">{getFrameworkInfo(framework).title}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">LLM Provider:</span>
                <span className="summary-value">{getLLMProviderInfo(llmProvider).title}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Python:</span>
                <span className="summary-value">{pythonVersion}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Deploy:</span>
                <span className="summary-value">{deploymentTarget}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Estrutura:</span>
                <span className="summary-value">{outputStructure}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Componentes:</span>
                <span className="summary-value">
                  {[
                    includeTests && 'Testes',
                    includeDocumentation && 'Docs',
                    includeLangfuseIntegration && 'Langfuse',
                    includeDocker && 'Docker',
                    includeKubernetes && 'K8s'
                  ].filter(Boolean).join(', ') || 'Básico'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-info">
            <span className="generation-estimate">⏱️ Tempo estimado: 2-5 minutos</span>
          </div>
          <div className="footer-actions">
            <button 
              className="btn-cancel" 
              onClick={onClose}
              disabled={isGenerating}
            >
              Cancelar
            </button>
            <button 
              className="btn-generate" 
              onClick={handleGenerate}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Gerando Código...
                </>
              ) : (
                <>
                  ⚡ Gerar Código Python
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeGenerationModal;