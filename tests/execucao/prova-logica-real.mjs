/**
 * Caso de teste — Passo 1 do plano, prova FIM-A-FIM.
 *
 * Pega a lógica REAL que a fábrica gravou no lugar do projeto, executa pelo
 * NOSSO processador de lugares, contra o servidor de agentes DE VERDADE.
 * Nada é simulado: o agente roda, lê e-mails e devolve.
 *
 * Uso:  node tests/execucao/prova-logica-real.mjs [projectId]
 */
import WebSocket from 'ws';
import { PlaceProcessor } from '../../src/components/petri-net/PlaceProcessor.js';

globalThis.WebSocket = WebSocket;                    // o navegador tem; o node não
const API = process.env.API_BASE || 'http://localhost:8000';
const PROJETO = process.argv[2] || '9a2c56de-ada5-4c49-b4a5-29bc237a590a';

const abrirRodada = (url) => new Promise((resolve, reject) => {
  const ws = new WebSocket(url);
  ws.on('open', () => ws.send(JSON.stringify({ type: 'iniciar_execucao', data: { projeto: 'teste' } })));
  ws.on('message', (m) => {
    const d = JSON.parse(m.toString());
    if (d.type === 'execucao_iniciada') { ws.close(); resolve(true); }
  });
  ws.on('error', reject);
  setTimeout(() => reject(new Error('sem resposta ao abrir a rodada')), 15000);
});

console.log('  buscando o projeto e a rede...');
const resp = await fetch(`${API}/api/projects/${PROJETO}`);
const rede = (await resp.json()).project.petriNet;
const lugar = rede.lugares.find(l => (l.logica || '').includes('execute_task'));
if (!lugar) { console.log('  FALHOU: nenhum lugar com lógica de conversa'); process.exit(1); }

const porta = (lugar.logica.match(/ws:\/\/localhost:(\d+)/) || [])[1];
const tarefa = (lugar.logica.match(/task_name["':\s]+["']([a-z_]+)/) || [])[1];
console.log(`  lugar ${lugar.id} (${(lugar.nome||'').replace(/\n/g,' ')}) -> tarefa "${tarefa}" na porta ${porta}`);
console.log(`  lógica: ${lugar.logica.length} caracteres, ${(lugar.logica.match(/await/g)||[]).length} esperas\n`);

console.log('  abrindo a rodada no servidor de agentes...');
await abrirRodada(`ws://localhost:${porta}`);
console.log('  rodada aberta.\n  executando a lógica real pelo NOSSO processador...');

const utils = {
  clone: (o) => JSON.parse(JSON.stringify(o || {})),
  now: () => new Date().toISOString(),
  merge: (a, b) => ({ ...a, ...b }),
  getPlaceOutput: () => ({})
};
const proc = new PlaceProcessor(rede, Object.fromEntries(rede.lugares.map(l => [l.id, l.tokens || 0])));
const entrada = { max_emails: 5, imap_server: 'imap.gmail.com', timeout_seconds: 30,
                  from_transition: 'T1', received_at: Date.now(), tokens_received: 1 };

const t0 = Date.now();
let saida;
try {
  saida = await proc.executeLogicCode(lugar.logica, {
    input: entrada, tokens: 1, places: rede.lugares, self: lugar, utils
  });
} catch (e) {
  console.log(`\n  FALHOU: ${e.constructor.name}: ${e.message}`); process.exit(1);
}
const seg = ((Date.now() - t0) / 1000).toFixed(1);

console.log(`\n  ===== RESULTADO (${seg}s) =====`);
console.log(`  status : ${saida.status}`);
console.log(`  campos : ${Object.keys(saida).join(', ')}`);

const falhas = [];
if (saida.status !== 'completed') falhas.push(`status veio "${saida.status}", esperado "completed"`);
if (saida.error) falhas.push(`veio erro: ${saida.error}`);
const novos = Object.keys(saida).filter(k => !(k in entrada));
if (novos.length === 0) falhas.push('a tarefa não acrescentou nenhum campo ao que entrou');
else console.log(`  a tarefa ACRESCENTOU: ${novos.join(', ')}`);

const bruto = JSON.stringify(saida);
const qtd = (bruto.match(/total_emails["':\s]+(\d+)/) || [])[1];
if (qtd) console.log(`  e-mails lidos de verdade: ${qtd}`);

if (falhas.length) { console.log('\n  FALHOU:'); falhas.forEach(f => console.log('   - ' + f)); process.exit(1); }
console.log('\n  PASSOU — a lógica real rodou pelo nosso processador contra o servidor de verdade.');
