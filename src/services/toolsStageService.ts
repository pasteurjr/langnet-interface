/**
 * Etapa FERRAMENTAS — cliente da API.
 *
 * A etapa resolve cada ferramenta citada na especificação de Agentes e Tarefas para uma
 * implementação REAL (biblioteca do gerador, servidor MCP ou função determinística com
 * contrato declarado). Ferramenta sem implementação bloqueia a geração de código.
 */
// As demais etapas usam REACT_APP_API_URL já COM o sufixo /api; aqui aceitamos as duas
// formas para não depender de como o ambiente foi configurado.
const RAIZ = process.env.REACT_APP_API_URL || "http://localhost:8003/api";
const BASE = RAIZ.replace(/\/api\/?$/, "");

export type OrigemFerramenta = "biblioteca" | "mcp" | "deterministica" | "externa" | "pendente";

export interface Ferramenta {
  nome: string;
  origem: OrigemFerramenta;
  resolvida: boolean;
  implementacao: string;
  descricao: string;
  entrada: string[];
  saida: string[];
  regra: string;
  usada_por: string[];
}

export interface ResumoFerramentas {
  total: number;
  resolvidas: number;
  pendentes: number;
}

export interface PortaoFerramentas {
  aprovado: boolean;
  pendentes: string[];
  mensagem: string;
}

export interface DocumentoFerramentas {
  tools: Ferramenta[];
  resumo: ResumoFerramentas;
  gate?: PortaoFerramentas;
}

export interface SessaoFerramentas extends DocumentoFerramentas {
  session_id: string;
  version: number;
}

function headers() {
  const token = localStorage.getItem("accessToken") || localStorage.getItem("token") || "";
  return { "Content-Type": "application/json", Authorization: `Bearer ${token}` };
}

async function pedir<T>(caminho: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${caminho}`, { ...init, headers: headers() });
  if (!r.ok) {
    const texto = await r.text();
    throw new Error(texto || `Falha na chamada ${caminho} (${r.status})`);
  }
  return (await r.json()) as T;
}

export const gerarFerramentas = (projectId: string, atsSessionId?: string) =>
  pedir<SessaoFerramentas>(`/api/tools-stage/${projectId}/generate`, {
    method: "POST",
    body: JSON.stringify({ agent_task_spec_session_id: atsSessionId || null }),
  });

export const ultimaSessao = (projectId: string) =>
  pedir<any>(`/api/tools-stage/project/${projectId}/latest`);

export const listarSessoes = (projectId: string) =>
  pedir<{ sessions: any[] }>(`/api/tools-stage/project/${projectId}/sessions`);

export const obterSessao = (sessionId: string) =>
  pedir<any>(`/api/tools-stage/${sessionId}`);

export const refinarFerramentas = (sessionId: string, instrucao: string) =>
  pedir<SessaoFerramentas>(`/api/tools-stage/${sessionId}/chat`, {
    method: "POST",
    body: JSON.stringify({ content: instrucao }),
  });

export const historicoChat = (sessionId: string) =>
  pedir<{ messages: { role: string; content: string; created_at: string }[] }>(
    `/api/tools-stage/${sessionId}/chat`);

export const salvarFerramentas = (sessionId: string, doc: DocumentoFerramentas, descricao?: string) =>
  pedir<SessaoFerramentas>(`/api/tools-stage/${sessionId}`, {
    method: "PUT",
    body: JSON.stringify({ tools_json: doc, change_description: descricao || "edição manual" }),
  });

export const listarVersoes = (sessionId: string) =>
  pedir<{ versions: { version: number; change_type: string; change_description: string; created_at: string }[] }>(
    `/api/tools-stage/${sessionId}/versions`);

export const obterVersao = (sessionId: string, versao: number) =>
  pedir<DocumentoFerramentas>(`/api/tools-stage/${sessionId}/versions/${versao}`);

export const aprovarFerramentas = (sessionId: string, aprovar = true) =>
  pedir<{ approval_status: string; gate: PortaoFerramentas }>(
    `/api/tools-stage/${sessionId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approve: aprovar }),
    });
