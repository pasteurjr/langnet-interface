/**
 * Modelo de linguagem que a APLICAÇÃO GERADA vai usar — escolha do projeto.
 *
 * Antes isso vinha do arquivo de ambiente da máquina que gerou: o pacote saía sempre apontando
 * para o modelo local e trocar exigia editar o arquivo à mão depois de gerar. A escolha passou a
 * ser do projeto, feita na interface, e vai para o pacote na próxima geração de código.
 */
const API = process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_URL || "http://localhost:8003/api";

export interface EscolhaLlm {
  provedor: string;
  modelo: string;
  endereco: string;
  max_tokens: number;
  chave_env: string;
  rotulo: string;
}

export interface ProvedorLlm {
  rotulo: string;
  modelo_padrao: string;
  endereco_padrao: string;
  chave_env: string;
  observacao: string;
}

export interface RespostaLlmApp {
  escolha: EscolhaLlm;
  provedores: Record<string, ProvedorLlm>;
}

const cabecalhos = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
});

export async function obterLlmDoApp(projectId: string): Promise<RespostaLlmApp> {
  const r = await fetch(`${API}/projects/${projectId}/app-llm`, { headers: cabecalhos() });
  if (!r.ok) throw new Error(`Falha ao ler a escolha de modelo (${r.status})`);
  return r.json();
}

export async function definirLlmDoApp(
  projectId: string,
  cfg: { provedor: string; modelo?: string; endereco?: string; max_tokens?: number }
): Promise<RespostaLlmApp> {
  const r = await fetch(`${API}/projects/${projectId}/app-llm`, {
    method: "PUT", headers: cabecalhos(), body: JSON.stringify(cfg),
  });
  if (!r.ok) throw new Error(`Falha ao gravar a escolha de modelo (${r.status})`);
  return r.json();
}
