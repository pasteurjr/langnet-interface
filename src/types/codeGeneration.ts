// src/types/codeGeneration.ts - Tipos específicos para Geração de Código Python

export enum CodeGenerationStatus {
    PENDING = 'pending',
    GENERATING = 'generating',
    GENERATED = 'generated',
    BUILDING = 'building',
    READY = 'ready',
    ERROR = 'error',
    DEPLOYING = 'deploying',
    DEPLOYED = 'deployed'
  }
  
  export enum FrameworkType {
    CREWAI = 'crewai',
    LANGCHAIN = 'langchain',
    AUTOGEN = 'autogen',
    CUSTOM = 'custom'
  }
  
  export enum MemorySystemType {
    LANGCHAIN_FULL = 'langchain_full',
    LANGCHAIN_SIMPLE = 'langchain_simple',
    REDIS = 'redis',
    POSTGRESQL = 'postgresql',
    INMEMORY = 'inmemory'
  }
  
  export enum LLMProviderType {
    OPENAI = 'openai',
    ANTHROPIC = 'anthropic',
    AZURE_OPENAI = 'azure_openai',
    HUGGINGFACE = 'huggingface',
    OLLAMA = 'ollama',
    CUSTOM = 'custom'
  }
  
  export enum PythonVersionType {
    PYTHON_39 = 'python3.9',
    PYTHON_310 = 'python3.10',
    PYTHON_311 = 'python3.11',
    PYTHON_312 = 'python3.12'
  }
  
  export enum DeploymentTargetType {
    LOCAL = 'local',
    DOCKER = 'docker',
    KUBERNETES = 'kubernetes',
    AWS = 'aws',
    AZURE = 'azure',
    GCP = 'gcp',
    VERCEL = 'vercel',
    HEROKU = 'heroku'
  }
  
  export interface CodeFile {
    id: string;
    name: string;
    path: string;
    type: 'python' | 'yaml' | 'json' | 'markdown' | 'dockerfile' | 'requirements' | 'config';
    content: string;
    size: number;
    isGenerated: boolean;
    isModified: boolean;
    lastModified: string;
    dependencies: string[];
    imports: string[];
    exports: string[];
    syntaxErrors: CodeValidationIssue[];
    lintingIssues: CodeValidationIssue[];
  }
  
  export interface CodeValidationIssue {
    id: string;
    type: 'syntax' | 'import' | 'linting' | 'security' | 'performance';
    severity: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
    rule?: string;
    suggestion?: string;
  }
  
  export interface PetriNetImplementation {
    id: string;
    name: string;
    className: string;
    places: PetriPlaceCode[];
    transitions: PetriTransitionCode[];
    stateClass: string;
    graphImplementation: string;
    executionEngine: string;
  }
  
  export interface PetriPlaceCode {
    id: string;
    name: string;
    variableName: string;
    initialTokens: number;
    dataType: string;
    validationRules: string[];
  }
  
  export interface PetriTransitionCode {
    id: string;
    name: string;
    functionName: string;
    agentId?: string;
    taskId?: string;
    guardCondition?: string;
    inputPlaces: string[];
    outputPlaces: string[];
    implementation: string;
  }
  
  export interface AgentImplementation {
    id: string;
    name: string;
    className: string;
    role: string;
    goal: string;
    backstory: string;
    tools: ToolImplementation[];
    llmConfig: LLMConfiguration;
    memoryConfig: MemoryConfiguration;
    executionConfig: ExecutionConfiguration;
    imports: string[];
    implementation: string;
  }
  
  export interface TaskImplementation {
    id: string;
    name: string;
    functionName: string;
    description: string;
    expectedOutput: string;
    agentId: string;
    inputSchema: JSONSchema;
    outputSchema: JSONSchema;
    context: string[];
    tools: string[];
    implementation: string;
    validationLogic: string;
    errorHandling: string;
  }
  
  export interface ToolImplementation {
    id: string;
    name: string;
    className: string;
    description: string;
    inputSchema: JSONSchema;
    outputSchema: JSONSchema;
    implementation: string;
    dependencies: string[];
    configuration: Record<string, any>;
  }
  
  export interface JSONSchema {
    type: string;
    properties: Record<string, any>;
    required: string[];
    additionalProperties: boolean;
  }
  
  export interface LLMConfiguration {
    provider: LLMProviderType;
    model: string;
    temperature: number;
    maxTokens: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
    apiKey: string;
    baseUrl?: string;
    timeout: number;
    retryAttempts: number;
  }
  
  export interface MemoryConfiguration {
    type: MemorySystemType;
    maxTokens: number;
    persistenceEnabled: boolean;
    connectionString?: string;
    redisConfig?: RedisConfig;
    postgresConfig?: PostgresConfig;
  }
  
  export interface RedisConfig {
    host: string;
    port: number;
    password?: string;
    database: number;
    ssl: boolean;
  }
  
  export interface PostgresConfig {
    host: string;
    port: number;
    database: string;
    username: string;
    password: string;
    ssl: boolean;
    poolSize: number;
  }
  
  export interface ExecutionConfiguration {
    maxIterations: number;
    timeout: number;
    retryAttempts: number;
    parallelExecution: boolean;
    errorHandling: 'strict' | 'lenient' | 'custom';
    loggingLevel: 'debug' | 'info' | 'warning' | 'error';
    monitoringEnabled: boolean;
    metricsCollection: boolean;
  }
  
  export interface TestConfiguration {
    generateTests: boolean;
    testFramework: 'pytest' | 'unittest' | 'nose2';
    coverageThreshold: number;
    integrationTests: boolean;
    performanceTests: boolean;
    mockExternalServices: boolean;
    testDataGeneration: boolean;
  }
  
  export interface BuildConfiguration {
    pythonVersion: PythonVersionType;
    packageManager: 'pip' | 'poetry' | 'conda';
    virtualEnvironment: boolean;
    requirements: string[];
    devRequirements: string[];
    buildTools: string[];
    linting: {
      enabled: boolean;
      tools: ('flake8' | 'black' | 'isort' | 'mypy' | 'pylint')[];
      configFiles: Record<string, string>;
    };
    formatting: {
      enabled: boolean;
      lineLength: number;
      indentSize: number;
      quotes: 'single' | 'double';
    };
  }
  
  export interface DeploymentConfiguration {
    target: DeploymentTargetType;
    dockerConfig?: DockerConfig;
    kubernetesConfig?: KubernetesConfig;
    cloudConfig?: CloudConfig;
    environmentVariables: Record<string, string>;
    secrets: Record<string, string>;
    healthChecks: HealthCheckConfig[];
    scaling: ScalingConfig;
  }
  
  export interface DockerConfig {
    baseImage: string;
    port: number;
    workingDirectory: string;
    entrypoint: string;
    environment: Record<string, string>;
    volumes: string[];
    networks: string[];
  }
  
  export interface KubernetesConfig {
    namespace: string;
    replicas: number;
    resources: {
      requests: { cpu: string; memory: string };
      limits: { cpu: string; memory: string };
    };
    service: {
      type: 'ClusterIP' | 'NodePort' | 'LoadBalancer';
      port: number;
      targetPort: number;
    };
    ingress?: {
      enabled: boolean;
      host: string;
      path: string;
      tls: boolean;
    };
  }
  
  export interface CloudConfig {
    provider: 'aws' | 'azure' | 'gcp';
    region: string;
    instanceType: string;
    autoScaling: boolean;
    loadBalancer: boolean;
    database: {
      type: string;
      size: string;
      backup: boolean;
    };
    storage: {
      type: string;
      size: string;
      encryption: boolean;
    };
  }
  
  export interface HealthCheckConfig {
    name: string;
    endpoint: string;
    method: 'GET' | 'POST' | 'HEAD';
    expectedStatus: number;
    timeout: number;
    interval: number;
    retries: number;
  }
  
  export interface ScalingConfig {
    enabled: boolean;
    minReplicas: number;
    maxReplicas: number;
    targetCPU: number;
    targetMemory: number;
    scaleUpDelay: number;
    scaleDownDelay: number;
  }
  
  export interface MonitoringIntegration {
    langfuseEnabled: boolean;
    langfuseConfig?: {
      publicKey: string;
      secretKey: string;
      host: string;
      enableTracing: boolean;
      sampleRate: number;
    };
    customMetrics: MetricDefinition[];
    alerting: AlertingConfig;
  }
  
  export interface MetricDefinition {
    name: string;
    type: 'counter' | 'gauge' | 'histogram' | 'summary';
    description: string;
    labels: string[];
    unit: string;
  }
  
  export interface AlertingConfig {
    enabled: boolean;
    channels: ('email' | 'slack' | 'webhook')[];
    rules: AlertRule[];
  }
  
  export interface AlertRule {
    name: string;
    condition: string;
    threshold: number;
    duration: string;
    severity: 'info' | 'warning' | 'critical';
    message: string;
  }
  
  export interface CodeGenerationRequest {
    projectId: string;
    petriNetId: string;
    agentIds: string[];
    taskIds: string[];
    framework: FrameworkType;
    memorySystem: MemorySystemType;
    llmProvider: LLMProviderType;
    pythonVersion: PythonVersionType;
    includeTests: boolean;
    includeDocumentation: boolean;
    includeLangfuseIntegration: boolean;
    buildConfig: BuildConfiguration;
    deploymentConfig: DeploymentConfiguration;
    testConfig: TestConfiguration;
    monitoringConfig: MonitoringIntegration;
    customInstructions?: string;
    outputStructure: 'package' | 'single_file' | 'microservices';
  }
  
  export interface CodeGenerationResult {
    id: string;
    projectId: string;
    status: CodeGenerationStatus;
    request: CodeGenerationRequest;
    files: CodeFile[];
    structure: ProjectStructure;
    buildLog: BuildLogEntry[];
    testResults?: TestResults;
    deploymentInfo?: DeploymentInfo;
    generatedAt: string;
    buildTime: number;
    metrics: GenerationMetrics;
    errors: CodeValidationIssue[];
    warnings: CodeValidationIssue[];
  }
  
  export interface ProjectStructure {
    rootPath: string;
    directories: DirectoryNode[];
    totalFiles: number;
    totalSize: number;
    packageInfo: PackageInfo;
  }
  
  export interface DirectoryNode {
    name: string;
    path: string;
    type: 'directory' | 'file';
    children?: DirectoryNode[];
    size?: number;
    isGenerated: boolean;
  }
  
  export interface PackageInfo {
    name: string;
    version: string;
    description: string;
    author: string;
    license: string;
    dependencies: Record<string, string>;
    devDependencies: Record<string, string>;
    scripts: Record<string, string>;
  }
  
  export interface BuildLogEntry {
    id: string;
    timestamp: string;
    level: 'debug' | 'info' | 'warning' | 'error';
    stage: 'generation' | 'validation' | 'building' | 'testing' | 'deployment';
    message: string;
    details?: any;
  }
  
  export interface TestResults {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    coverage: number;
    duration: number;
    testFiles: TestFileResult[];
  }
  
  export interface TestFileResult {
    fileName: string;
    tests: TestCaseResult[];
    coverage: number;
    duration: number;
  }
  
  export interface TestCaseResult {
    name: string;
    status: 'passed' | 'failed' | 'skipped';
    duration: number;
    error?: string;
    assertions: number;
  }
  
  export interface DeploymentInfo {
    target: DeploymentTargetType;
    status: 'pending' | 'deploying' | 'deployed' | 'failed';
    url?: string;
    endpoints: string[];
    resources: DeployedResource[];
    logs: DeploymentLogEntry[];
    deployedAt?: string;
  }
  
  export interface DeployedResource {
    type: string;
    name: string;
    status: string;
    url?: string;
    metadata: Record<string, any>;
  }
  
  export interface DeploymentLogEntry {
    timestamp: string;
    level: 'info' | 'warning' | 'error';
    message: string;
    resource?: string;
  }
  
  export interface GenerationMetrics {
    linesOfCode: number;
    numberOfFiles: number;
    numberOfClasses: number;
    numberOfFunctions: number;
    cyclomaticComplexity: number;
    maintainabilityIndex: number;
    testCoverage: number;
    codeQualityScore: number;
    securityScore: number;
    performanceScore: number;
  }
  
  export interface CodeExecutionSession {
    id: string;
    name: string;
    status: 'idle' | 'running' | 'completed' | 'error' | 'stopped';
    startTime: string;
    endTime?: string;
    input: any;
    output?: any;
    logs: ExecutionLogEntry[];
    metrics: ExecutionMetrics;
    petriNetState: PetriNetExecutionState;
  }
  
  export interface ExecutionLogEntry {
    timestamp: string;
    level: 'debug' | 'info' | 'warning' | 'error';
    source: 'system' | 'agent' | 'task' | 'petri_net';
    agentId?: string;
    taskId?: string;
    transitionId?: string;
    message: string;
    data?: any;
  }
  
  export interface ExecutionMetrics {
    duration: number;
    tokensUsed: number;
    apiCalls: number;
    memoryUsage: number;
    cpuUsage: number;
    transitionsExecuted: number;
    agentsActivated: number;
    tasksCompleted: number;
    errorsCount: number;
    warningsCount: number;
  }
  
  export interface PetriNetExecutionState {
    currentPlaces: Record<string, number>;
    enabledTransitions: string[];
    executionHistory: TransitionExecution[];
    deadlocks: string[];
    completedPaths: string[];
  }
  
  export interface TransitionExecution {
    transitionId: string;
    timestamp: string;
    inputTokens: Record<string, number>;
    outputTokens: Record<string, number>;
    executionTime: number;
    agentId?: string;
    taskId?: string;
    result: 'success' | 'error' | 'timeout';
    error?: string;
  } 