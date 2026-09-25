/**
 * Caso de teste — Passo 1 do plano de execução.
 *
 * PROVA que o processador de lugares consegue executar a lógica que a nossa
 * própria fábrica escreve, que é baseada em ESPERA (await).
 *
 * Cada caso é o que um lugar real faz, em ordem crescente de fidelidade:
 *   1. lógica simples, sem espera        -> tem de passar sempre (controle)
 *   2. lógica que espera um tempo        -> a forma mínima de espera
 *   3. lógica que espera uma conversa    -> exatamente o que a fábrica gera
 *   4. lógica que junta o lugar anterior -> o laço de espera por predecessor
 *   5. lógica que falha                  -> o erro tem de chegar como erro
 *
 * Uso:  node tests/execucao/prova-lugar-espera.mjs
 */
import { PlaceProcessor } from '../../src/components/petri-net/PlaceProcessor.js';

const rede = {
  lugares: [
    { id: 'P1', nome: 'inicio', tokens: 1, logica: '' },
    { id: 'P2', nome: 'tarefa', tokens: 0, logica: '' }
  ],
  transicoes: [{ id: 'T1', nome: 't' }],
  arcos: [{ origem: 'P1', destino: 'T1' }, { origem: 'T1', destino: 'P2' }]
};

// Servidor de mentira: responde como o servidor de agentes real responde.
class ConversaDeMentira {
  constructor(url) {
    this.url = url;
    this.onopen = null; this.onmessage = null; this.onerror = null; this.onclose = null;
    setTimeout(() => this.onopen && this.onopen(), 0);
  }
  send(texto) {
    const pedido = JSON.parse(texto);
    setTimeout(() => {
      this.onmessage && this.onmessage({ data: JSON.stringify({
        type: 'task_completed',
        data: { task_name: pedido.data.task_name, success: true, duration: 0.05,
                result: { emails_json: '{"total_emails":5}', total_emails: 5 } }
      })});
    }, 120);
  }
  close() {}
}
globalThis.WebSocket = ConversaDeMentira;

const utils = {
  clone: (o) => JSON.parse(JSON.stringify(o || {})),
  now:   () => new Date().toISOString(),
  merge: (a, b) => ({ ...a, ...b }),
  getPlaceOutput: (id) => (globalThis.__saidas || {})[id] || {}
};

const CASOS = [
  {
    nome: '1. lógica simples, sem espera (controle)',
    logica: `const output = utils.clone(input); output.marcado = true; return output;`,
    confere: (r) => r && r.marcado === true
  },
  {
    nome: '2. lógica que espera um tempo',
    logica: `const output = utils.clone(input);
             await new Promise(r => setTimeout(r, 50));
             output.esperou = true; return output;`,
    confere: (r) => r && r.esperou === true
  },
  {
    nome: '3. lógica que espera uma conversa (o que a fábrica gera)',
    logica: `const output = utils.clone(input);
             const ws = new WebSocket("ws://localhost:9999");
             const result = await new Promise((resolve, reject) => {
               const t = setTimeout(() => { ws.close(); reject(new Error('timeout')); }, 5000);
               ws.onopen = () => ws.send(JSON.stringify({ type:'execute_task',
                 data: { task_name: 'read_email', input_data: output } }));
               ws.onmessage = (e) => { const r = JSON.parse(e.data);
                 if (r.type === 'task_completed') { clearTimeout(t); ws.close();
                   resolve((r.data && r.data.result) || r.data || {}); } };
               ws.onerror = () => { clearTimeout(t); reject(new Error('erro')); };
             });
             Object.assign(output, result); output.status = 'completed'; return output;`,
    confere: (r) => r && r.status === 'completed' && r.total_emails === 5
  },
  {
    nome: '4. lógica que junta o lugar anterior (laço de espera)',
    prepara: () => { globalThis.__saidas = {};
                     setTimeout(() => { globalThis.__saidas = { P1: { vindo_de_tras: 42 } }; }, 150); },
    logica: `const output = utils.clone(input);
             const limite = Date.now() + 3000;
             let anterior = utils.getPlaceOutput('P1');
             while (!anterior.vindo_de_tras && Date.now() < limite) {
               await new Promise(r => setTimeout(r, 40));
               anterior = utils.getPlaceOutput('P1');
             }
             Object.assign(output, anterior); return output;`,
    confere: (r) => r && r.vindo_de_tras === 42
  },
  {
    nome: '5. lógica que falha — o erro tem de chegar como erro',
    logica: `await new Promise(r => setTimeout(r, 20));
             throw new Error('falha proposital');`,
    esperaErro: 'falha proposital'
  }
];

const proc = new PlaceProcessor(rede, { P1: 1, P2: 0 });
let ok = 0, falhou = 0;

for (const caso of CASOS) {
  if (caso.prepara) caso.prepara();
  const contexto = { input: { origem: 'teste' }, tokens: 1, places: rede.lugares,
                     self: rede.lugares[1], utils };
  try {
    const r = await proc.executeLogicCode(caso.logica, contexto);
    if (caso.esperaErro) {
      console.log(`  FALHOU  ${caso.nome}\n          esperava erro "${caso.esperaErro}", veio resultado`);
      falhou++;
    } else if (caso.confere(r)) {
      console.log(`  passou  ${caso.nome}`);
      ok++;
    } else {
      console.log(`  FALHOU  ${caso.nome}\n          resultado inesperado: ${JSON.stringify(r).slice(0,120)}`);
      falhou++;
    }
  } catch (e) {
    if (caso.esperaErro && String(e.message).includes(caso.esperaErro)) {
      console.log(`  passou  ${caso.nome}`);
      ok++;
    } else {
      console.log(`  FALHOU  ${caso.nome}\n          ${e.constructor.name}: ${e.message}`);
      falhou++;
    }
  }
}

console.log(`\n  ${ok} de ${CASOS.length} casos passaram, ${falhou} falharam`);
process.exit(falhou === 0 ? 0 : 1);
