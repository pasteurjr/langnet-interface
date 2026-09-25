/**
 * Caso de teste — Passo 3, prova do lado da FÁBRICA.
 *
 * Pega o JavaScript que o gerador emite para cada lugar (rede em
 * tmp/rede_gerada.json) e roda no NOSSO motor, com o lugar anterior falhando.
 * A cadeia tem de PARAR e dizer o motivo — não seguir com lixo.
 *
 * Uso:  node tests/execucao/prova-falha-codigo-gerado.mjs
 */
import fs from 'fs';
import WebSocket from 'ws';
import { PetriNetSimulator } from '../../src/components/petri-net/PetriNetSimulator.js';

globalThis.WebSocket = WebSocket;
const espera = (ms) => new Promise(r => setTimeout(r, ms));
const res = [];
const confere = (nome, ok, det = '') => {
  res.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !det ? '' : '\n          ' + det}`);
};

const rede = JSON.parse(fs.readFileSync('/home/pasteurjr/.claude/jobs/db3adebd/tmp/rede_gerada.json', 'utf8'));
console.log(`  rede gerada pela fábrica: ${rede.lugares.length} lugares, código de ${rede.lugares[0].logica.length} caracteres cada\n`);

// O lugar do meio vai falhar: apontamos a conversa dele para uma porta morta.
const p2 = rede.lugares.find(l => l.id === 'P2');
p2.logica = p2.logica.replace(/ws:\/\/localhost:\$\{PORT\}/, 'ws://localhost:6399')
                     .replace(/const PORT = \d+;/, 'const PORT = 6399;')
                     .replace(/const TIMEOUT_MS = \d+;/, 'const TIMEOUT_MS = 2500;');

const sim = new PetriNetSimulator(rede);
sim.startSimulation();
await espera(300);
sim.fireTransition('T1');
await espera(6000);

const l2 = sim.petriNet.lugares.find(l => l.id === 'P2');
confere('1. o lugar que não conseguiu falar com o servidor fica marcado como ERRO',
        l2.status === 'error', `estado ficou "${l2.status}"`);
confere('2. o motivo fica registrado',
        typeof l2.error === 'string' && l2.error.length > 0, `motivo: ${JSON.stringify(l2.error)}`);
confere('3. a transição seguinte NÃO libera',
        sim.isTransitionEnabled('T2') === false,
        'T2 liberou com o lugar anterior tendo falhado');

// Forçamos o disparo para provar a segunda barreira: mesmo que alguém dispare,
// o código GERADO do lugar seguinte tem de recusar o predecessor em erro.
try { sim.fireTransition('T2'); } catch (e) { /* esperado: não está apta */ }
await espera(4000);
const l3 = sim.petriNet.lugares.find(l => l.id === 'P3');
const naoFingiu = l3.status !== 'completed' || !!(l3.output_data && l3.output_data.error);
confere('4. o lugar seguinte não finge que trabalhou sobre dado que não existe',
        naoFingiu,
        `estado de P3: "${l3.status}" saída: ${JSON.stringify(l3.output_data || {}).slice(0,140)}`);

const ok = res.filter(Boolean).length;
console.log(`\n  ${ok} de ${res.length} casos passaram, ${res.length - ok} falharam`);
process.exit(ok === res.length ? 0 : 1);
