/**
 * Caso de teste — Passo 2, prova FIM-A-FIM.
 *
 * Usa a rede REAL do projeto e o servidor de agentes REAL. Dispara a primeira
 * transição e vigia, segundo a segundo, se a transição SEGUINTE fica apta
 * enquanto o agente ainda está trabalhando. Não pode ficar.
 *
 * Uso:  node tests/execucao/prova-concluido-real.mjs [projectId]
 */
import WebSocket from 'ws';
import { PetriNetSimulator } from '../../src/components/petri-net/PetriNetSimulator.js';

globalThis.WebSocket = WebSocket;
const API = process.env.API_BASE || 'http://localhost:8000';
const PROJETO = process.argv[2] || '9a2c56de-ada5-4c49-b4a5-29bc237a590a';
const espera = (ms) => new Promise(r => setTimeout(r, ms));

const abrirRodada = (url) => new Promise((resolve, reject) => {
  const ws = new WebSocket(url);
  ws.on('open', () => ws.send(JSON.stringify({ type: 'iniciar_execucao', data: { projeto: 'teste' } })));
  ws.on('message', (m) => { if (JSON.parse(m.toString()).type === 'execucao_iniciada') { ws.close(); resolve(); } });
  ws.on('error', reject);
  setTimeout(() => reject(new Error('sem resposta ao abrir a rodada')), 15000);
});

const rede = (await (await fetch(`${API}/api/projects/${PROJETO}`)).json()).project.petriNet;
const comLogica = rede.lugares.find(l => (l.logica || '').includes('execute_task'));
const porta = (comLogica.logica.match(/ws:\/\/localhost:(\d+)/) || [])[1];

// transição que vem DEPOIS do lugar com lógica
const tDepois = rede.arcos.find(a => a.origem === comLogica.id)?.destino;
const tAntes  = rede.arcos.find(a => a.destino === comLogica.id)?.origem;
console.log(`  rede: ${rede.lugares.length} lugares, ${rede.transicoes.length} transições`);
console.log(`  lugar com agente: ${comLogica.id} (${(comLogica.nome||'').replace(/\n/g,' ')})`);
console.log(`  transição antes: ${tAntes}   |   transição depois: ${tDepois}   |   porta ${porta}\n`);

await abrirRodada(`ws://localhost:${porta}`);
console.log('  rodada aberta no servidor de agentes.');

const sim = new PetriNetSimulator(rede);
const falhas = [];

if (!sim.isTransitionEnabled(tAntes)) falhas.push(`${tAntes} deveria estar apta no início`);
console.log(`  disparando ${tAntes}...`);
sim.fireTransition(tAntes);

// vigia enquanto o agente trabalha
const t0 = Date.now();
let aptaCedo = false, amostras = 0, segConcluiu = null;
while (Date.now() - t0 < 180000) {
  await espera(1000);
  amostras++;
  const rodando = sim.placeProcessor.isProcessing(comLogica.id);
  const apta = sim.isTransitionEnabled(tDepois);
  if (rodando && apta) { aptaCedo = true; break; }
  if (!rodando) { segConcluiu = ((Date.now() - t0) / 1000).toFixed(1); break; }
}

console.log(`  vigiei ${amostras} vezes, de segundo em segundo, enquanto o agente trabalhava.`);
if (aptaCedo) falhas.push(`${tDepois} ficou APTA com ${comLogica.id} ainda rodando`);
else console.log(`  em nenhuma delas ${tDepois} ficou apta — correto.`);

if (segConcluiu) console.log(`  ${comLogica.id} concluiu em ${segConcluiu}s.`);
else falhas.push('o lugar não concluiu em 180s');

await espera(500);
const status = sim.petriNet.lugares.find(l => l.id === comLogica.id).status;
const aptaAgora = sim.isTransitionEnabled(tDepois);
console.log(`  estado de ${comLogica.id}: "${status}"   |   ${tDepois} apta agora: ${aptaAgora}`);
if (status !== 'completed') falhas.push(`estado ficou "${status}", esperado "completed"`);
if (!aptaAgora) falhas.push(`${tDepois} continuou inapta depois de concluir — a rede travaria`);

const saida = sim.petriNet.lugares.find(l => l.id === comLogica.id).output_data || {};
const novos = Object.keys(saida).filter(k => !['from_transition','received_at','tokens_received','max_emails','imap_server','timeout_seconds'].includes(k));
console.log(`  saída do lugar acrescentou: ${novos.slice(0,8).join(', ')}${novos.length>8?', …':''}`);
if (novos.length === 0) falhas.push('o lugar não produziu nada — saída é cópia da entrada');

if (falhas.length) { console.log('\n  FALHOU:'); falhas.forEach(f => console.log('   - ' + f)); process.exit(1); }
console.log('\n  PASSOU — na rede real, a transição seguinte só ficou apta depois do agente terminar.');
