/**
 * Deployment Service
 * Comunicação com /api/code-generation/* — implanta o sistema gerado (sobe servidor de
 * agentes + API + interface), acompanha o estado e lê o log ao vivo.
 */
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  return { 'Content-Type': 'application/json', Authorization: token ? `Bearer ${token}` : '' };
};

/** Recusa do portão: a implantação foi barrada porque a geração tem lacuna conhecida. */
export class ReprovadoNoPortao extends Error {
  portoes: PortoesVeredito;
  resumo: string[];
  comoProsseguir: string;
  constructor(detalhe: any) {
    super(detalhe?.erro || 'geração reprovada nos portões');
    this.name = 'ReprovadoNoPortao';
    this.portoes = detalhe?.portoes || {};
    this.resumo = detalhe?.resumo || [];
    this.comoProsseguir = detalhe?.como_prosseguir || '';
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: getAuthHeaders(), ...init });
  if (!res.ok) {
    const texto = await res.text();
    // 409 = portão: a resposta traz o veredito estruturado, não é erro de rede.
    if (res.status === 409) {
      try {
        const d = JSON.parse(texto);
        throw new ReprovadoNoPortao(d.detail || d);
      } catch (e) {
        if (e instanceof ReprovadoNoPortao) throw e;
      }
    }
    throw new Error(`${res.status}: ${texto.slice(0, 300)}`);
  }
  return res.json();
}

/** Um portão: o que ele confere, quantas pendências achou e quais. */
export interface Portao {
  reprovado: boolean;
  quantidade: number;
  descricao: string;
  itens: any[];
}

export interface PortoesVeredito {
  reprovado?: boolean;
  logica?: Portao;
  ferramentas?: Portao;
  contrato_tela?: Portao;
}

/** Onde se conserta cada tipo de pendência — sem isto o painel vira um muro. */
export const ONDE_CORRIGIR: Record<string, { etapa: string; caminho: string }> = {
  logica: { etapa: 'Agentes & Tarefas', caminho: 'agent-task' },
  ferramentas: { etapa: 'Ferramentas', caminho: 'tools-stage' },
  contrato_tela: { etapa: 'Interface & Protótipo', caminho: 'ui-spec' },
};

/** Veredito dos portões guardado junto com a geração. */
export const getPortoes = async (sessionId: string): Promise<PortoesVeredito> => {
  const d = await req<any>(`/code-generation/${sessionId}`);
  let meta = d?.execution_metadata || {};
  if (typeof meta === 'string') { try { meta = JSON.parse(meta); } catch (e) { meta = {}; } }
  return meta.portoes || {};
};

export interface DeployedService { name: string; port: number; url: string; }

export interface DeploymentRun {
  run_id: string;
  session_id: string;
  /** preparing | installing | running | stopped | crashed */
  status: string;
  started_at: string;
  finished_at: string;
  exit_code: number | null;
  work_dir: string;
  total_lines: number;
  services: DeployedService[];
  session_created_at?: string;
  stdout_tail?: string[];
}

export interface RunLogs {
  run_id: string; status: string; offset: number; total: number;
  lines: string[]; services: DeployedService[];
}

export interface EnvItem { key: string; value: string; }

/** Modelo de configuração do pacote gerado (.env.example) — pré-preenche o formulário. */
export const getEnvTemplate = (sessionId: string) =>
  req<{ session_id: string; items: EnvItem[]; raw: string }>(
    `/code-generation/${sessionId}/env-template`);

/**
 * Implanta a versão gerada. `env` é a configuração informada pelo operador (banco,
 * provedor de LLM, chaves) — o pacote gerado não traz segredo.
 */
export const startDeployment = (sessionId: string, env: Record<string, string> = {}, forcar = false) =>
  req<DeploymentRun>(`/code-generation/${sessionId}/run`, {
    method: 'POST', body: JSON.stringify({ env, forcar }),
  });

export const getDeployment = (runId: string) =>
  req<DeploymentRun>(`/code-generation/run/${runId}/status`);

export const stopDeployment = (runId: string) =>
  req<DeploymentRun>(`/code-generation/run/${runId}/stop`, { method: 'POST' });

/** Leitura incremental do log: pede só o que ainda não foi lido. */
export const getDeploymentLogs = (runId: string, offset = 0, limit = 500) =>
  req<RunLogs>(`/code-generation/run/${runId}/logs?offset=${offset}&limit=${limit}`);

/** Implantações do projeto (todas as sessões), mais recentes primeiro. */
export const listProjectDeployments = (projectId: string) =>
  req<{ runs: DeploymentRun[]; sessions: { id: string; created_at: string }[] }>(
    `/code-generation/project/${projectId}/runs`);

// ── Leitura dos eventos de tarefa a partir do log da implantação ────────────────
export interface TaskEvent {
  kind: 'INICIO' | 'OK' | 'ERRO';
  task: string; agent?: string; mode?: string; seconds?: number; error?: string;
}

/** O servidor de agentes escreve `[task] INICIO|OK|ERRO ...`; aqui isso vira evento. */
export function parseTaskEvents(lines: string[]): TaskEvent[] {
  const out: TaskEvent[] = [];
  for (const raw of lines) {
    const l = raw.replace(/^\[ws\]\s*/, '').trim();
    let m = l.match(/^\[task\] INICIO (\S+) agente=(\S+) modo=(\S+)/);
    if (m) { out.push({ kind: 'INICIO', task: m[1], agent: m[2], mode: m[3] }); continue; }
    m = l.match(/^\[task\] OK (\S+) em ([\d.]+)s/);
    if (m) { out.push({ kind: 'OK', task: m[1], seconds: parseFloat(m[2]) }); continue; }
    m = l.match(/^\[task\] ERRO (\S+) em ([\d.]+)s: (.*)$/);
    if (m) { out.push({ kind: 'ERRO', task: m[1], seconds: parseFloat(m[2]), error: m[3] }); }
  }
  return out;
}

export interface McpCall { tool: string; args: string; fields: string; }

/** Chamadas às ferramentas externas (MCP), como o servidor de agentes as registra. */
export function parseMcpCalls(lines: string[]): McpCall[] {
  const out: McpCall[] = [];
  for (const raw of lines) {
    const m = raw.match(/\[MCP prefetch\]\s+(\w+)\((.*?)\)\s*->\s*\+\[(.*?)\]/);
    if (m) out.push({ tool: m[1], args: m[2], fields: m[3] });
  }
  return out;
}

export interface TaskStat {
  task: string; agent: string; mode: string;
  runs: number; ok: number; erros: number; lastSeconds?: number; lastError?: string;
}

/** Consolida os eventos por tarefa — é o painel do Monitoramento. */
export function summarizeTasks(events: TaskEvent[]): TaskStat[] {
  const by = new Map<string, TaskStat>();
  for (const e of events) {
    const s = by.get(e.task) || { task: e.task, agent: '-', mode: '-', runs: 0, ok: 0, erros: 0 };
    if (e.kind === 'INICIO') { s.runs += 1; s.agent = e.agent || s.agent; s.mode = e.mode || s.mode; }
    if (e.kind === 'OK') { s.ok += 1; s.lastSeconds = e.seconds; }
    if (e.kind === 'ERRO') { s.erros += 1; s.lastSeconds = e.seconds; s.lastError = e.error; }
    by.set(e.task, s);
  }
  return Array.from(by.values()).sort((a, b) => b.runs - a.runs || a.task.localeCompare(b.task));
}
