/**
 * Caso de teste — Passo 5 do plano de execução.
 *
 * PROVA a peça que eu não conhecia e que faz a cadeia funcionar: por baixo,
 * há UMA conversa só com o servidor de agentes, com FILA e CACHE.
 * Sem ela, cada lugar abriria sua própria ligação: conversas duplicadas,
 * resultados fora de ordem e nada de cache para a tarefa seguinte.
 *
 *   1. várias tarefas usam UMA única ligação
 *   2. as tarefas são atendidas EM ORDEM (fila), não todas de uma vez
 *   3. o resultado de cada tarefa fica guardado para quem vier depois
 *   4. o interceptador entrega a mesma interface de sempre a quem chama
 *
 * Uso:  node tests/execucao/prova-conversa-unica.mjs
 */
import { WebSocketServer } from 'ws';
import WebSocket from 'ws';

globalThis.WebSocket = WebSocket;
const PORTA = 6402;
const res = [];
const confere = (nome, ok, det = '') => {
  res.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !det ? '' : '\n          ' + det}`);
};

// ---- servidor de mentira que conta quantas ligações recebeu ----
let ligacoes = 0;
const atendidas = [];
const servidor = new WebSocketServer({ port: PORTA });
servidor.on('connection', (ws) => {
  ligacoes++;
  ws.send(JSON.stringify({ type: 'welcome', supported_tasks: ['a', 'b', 'c'] }));
  ws.on('message', (m) => {
    const p = JSON.parse(m.toString());
    if (p.type === 'iniciar_execucao') {
      ws.send(JSON.stringify({ type: 'execucao_iniciada', success: true }));
      return;
    }
    if (p.type !== 'execute_task') return;
    const nome = p.data.task_name;
    atendidas.push({ nome, em: Date.now() });
    // demora diferente por tarefa, para expor atropelo de ordem
    const demora = nome === 'a' ? 500 : 120;
    setTimeout(() => {
      ws.send(JSON.stringify({ type: 'execution_step', data: { step_type: 'andamento', task_name: nome } }));
      ws.send(JSON.stringify({ type: 'task_completed', data: { task_name: nome, success: true,
                                                               result: { quem: nome, valor: nome.toUpperCase() } } }));
    }, demora);
  });
});
await new Promise(r => setTimeout(r, 300));

globalThis.window = { V7_WS_URI: `ws://localhost:${PORTA}` };
globalThis.localStorage = { getItem: () => null, setItem: () => {} };

const { CentralWSClient } = await import('../../src/components/petri-net/utils_exec/centralWSClient.js');
const cliente = CentralWSClient.getInstance();

// dispara três tarefas "ao mesmo tempo", como três lugares fariam
const t0 = Date.now();
const resultados = await Promise.all(['a', 'b', 'c'].map(n => cliente.executeTask(n, { pedido: n })));
const gasto = Date.now() - t0;

confere('1. várias tarefas usam UMA única ligação',
        ligacoes === 1, `o servidor recebeu ${ligacoes} ligações`);

const ordem = atendidas.map(x => x.nome).join(',');
confere('2. as tarefas são atendidas EM ORDEM (fila)',
        ordem === 'a,b,c',
        `ordem de chegada no servidor: ${ordem} — a fila não segurou`);

const cacheOk = ['a','b','c'].every(n => {
  const c = cliente.taskResults && cliente.taskResults[n];
  return c && JSON.stringify(c).includes(n.toUpperCase());
});
confere('3. o resultado de cada tarefa fica guardado para quem vier depois',
        cacheOk, `cache: ${JSON.stringify(Object.keys(cliente.taskResults || {}))}`);

const { FakeWebSocket } = await import('../../src/components/petri-net/utils_exec/fakeWebSocket.js');
const falsa = new FakeWebSocket(`ws://localhost:${PORTA}`);
const temInterface = ['send','close'].every(m => typeof falsa[m] === 'function')
                  && 'onopen' in falsa && 'onmessage' in falsa;
confere('4. o interceptador entrega a mesma interface de sempre a quem chama',
        temInterface, `métodos: ${Object.keys(falsa).join(', ')}`);

console.log(`\n  três tarefas em ${gasto}ms, uma ligação, ${atendidas.length} atendimentos`);
servidor.close();
const ok = res.filter(Boolean).length;
console.log(`\n  ${ok} de ${res.length} casos passaram, ${res.length - ok} falharam`);
process.exit(ok === res.length ? 0 : 1);
