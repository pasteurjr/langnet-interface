// Serviço de Configurações do Sistema (F1 / UC-P01)
// Consome /api/settings: leitura (segredos mascarados), gravação, e testes de conexão reais.
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function getToken(): string | null {
  return localStorage.getItem('accessToken') || localStorage.getItem('token');
}

function headers() {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    Authorization: token ? `Bearer ${token}` : '',
  };
}

export interface DatabaseSettings {
  db_host: string;
  db_port: string;
  db_user: string;
  db_password: string;        // sempre "" na leitura
  db_password_is_set?: boolean;
  db_name: string;
}

export interface LlmSettings {
  llm_provider: string;
  lmstudio_api_base: string;
  lmstudio_model_name: string;
  openai_api_key: string;     // sempre "" na leitura
  openai_api_key_is_set?: boolean;
  openai_model_name: string;
  deepseek_api_key: string;   // sempre "" na leitura
  deepseek_api_key_is_set?: boolean;
  deepseek_api_base: string;
  deepseek_model_name: string;
}

export interface SystemSettings {
  database: DatabaseSettings;
  llm: LlmSettings;
}

export interface TestResult {
  ok: boolean;
  message?: string;
  error?: string;
  model_found?: boolean;
  models_sample?: string[];
  endpoint?: string;
}

export async function getSettings(): Promise<SystemSettings> {
  const r = await fetch(`${API_BASE_URL}/settings`, { headers: headers() });
  if (!r.ok) throw new Error(`Falha ao carregar configurações (${r.status})`);
  return r.json();
}

export async function updateSettings(settings: Partial<SystemSettings>): Promise<{ status: string; written: number }> {
  const r = await fetch(`${API_BASE_URL}/settings`, {
    method: 'PUT',
    headers: headers(),
    body: JSON.stringify({ settings }),
  });
  if (!r.ok) throw new Error(`Falha ao salvar configurações (${r.status})`);
  return r.json();
}

export async function testDb(payload: Partial<DatabaseSettings>): Promise<TestResult> {
  const r = await fetch(`${API_BASE_URL}/settings/test-db`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload),
  });
  return r.json();
}

export async function testLlm(payload: {
  provider?: string; api_base?: string; model?: string; api_key?: string;
}): Promise<TestResult> {
  const r = await fetch(`${API_BASE_URL}/settings/test-llm`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(payload),
  });
  return r.json();
}
