/**
 * F0 — a rede de Petri INTEIRA do projeto, lugar por lugar, contra um servidor de agentes real.
 *
 * Usa o mesmo processador de lugares da Bancada do LangNet. Cada lugar roda a sua `logica`
 * gerada (que fala com o servidor de agentes), e a saída de um lugar é a entrada do seguinte,
 * como os arcos determinam. Passa se o token chega ao fim com todos os lugares concluídos.
 *
 * Uso: node --import ./tests/execucao/registrar.mjs tests/execucao/prova-rede-inteira.mjs <petri_net.json> <porta> <json-semente>
 */
import fs from 'fs';
import WebSocket from 'ws';
import { PlaceProcessor } from '../../src/components/petri-net/PlaceProcessor.js';
globalThis.WebSocket = WebSocket;

const [arquivo, porta, semente] = process.argv.slice(2);
const rede = JSON.parse(fs.readFileSync(arquivo, 'utf8'));
for (const l of rede.lugares) if (l.logica) l.logica = l.logica.replace(/ws:\/\/localhost:\d+/g, `ws://localhost:${porta}`).replace(/PORT\s*=\s*\d+/g, `PORT = ${porta}`);

await new Promise((ok, falha) => {
  const ws = new WebSocket(`ws://localhost:${porta}`);
  ws.on('open', () => ws.send(JSON.stringify({ type: 'iniciar_execucao', data: { projeto: 'prova-f0' } })));
  ws.on('message', (m) => { if (JSON.parse(m.toString()).type === 'execucao_iniciada') { ws.close(); ok(); } });
  ws.on('error', falha); setTimeout(() => falha(new Error('sem resposta ao abrir a rodada')), 15000);
});

// ordem pelos arcos: lugar → transição → lugar
const proximo = (id) => {
  const t = (rede.arcos || []).find(a => a.origem === id || a.source === id);
  if (!t) return null;
  const tid = t.destino || t.target;
  const p = (rede.arcos || []).find(a => (a.origem || a.source) === tid);
  return p ? (p.destino || p.target) : null;
};
const inicio = rede.lugares.find(l => (l.tokens || 0) > 0) || rede.lugares[0];
const utils = { clone: (o) => JSON.parse(JSON.stringify(o || {})), now: () => new Date().toISOString(), merge: (a, b) => ({ ...a, ...b }), getPlaceOutput: () => ({}) };
const proc = new PlaceProcessor(rede, Object.fromEntries(rede.lugares.map(l => [l.id, l.tokens || 0])));

let entrada = { ...JSON.parse(semente || '{}'), from_transition: 'T_start', received_at: Date.now(), tokens_received: 1 };
let id = inicio.id, passos = 0, falhas = [];
while (id && passos < 50) {
  const lugar = rede.lugares.find(l => l.id === id); passos++;
  if (lugar.logica && lugar.logica.includes('execute_task')) {
    const tarefa = (lugar.logica.match(/task_name["':\s]+["']([a-z_]+)/) || [])[1];
    const t0 = Date.now();
    let saida;
    try { saida = await proc.executeLogicCode(lugar.logica, { input: entrada, tokens: 1, places: rede.lugares, self: lugar, utils }); }
    catch (e) { saida = { status: 'erro', error: e.message }; }
    const s = ((Date.now() - t0) / 1000).toFixed(0);
    const ok = saida && saida.status === 'completed' && !saida.error;
    console.log(`${ok ? 'OK   ' : 'FALHA'} ${id} ${tarefa} (${s}s) status=${saida && saida.status}${saida && saida.error ? ' erro=' + String(saida.error).slice(0, 120) : ''}`);
    if (!ok) { falhas.push(`${id} ${tarefa}`); break; }   // falha bloqueia a transição seguinte
    entrada = { ...saida, from_transition: id, received_at: Date.now(), tokens_received: 1 };
  }
  const p = proximo(id);
  if (!p) { console.log(`token chegou ao fim em ${id}`); break; }
  id = p;
}
console.log(`\nlugares percorridos: ${passos} | falharam: ${falhas.length}`);
process.exit(falhas.length ? 1 : 0);
