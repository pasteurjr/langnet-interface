/**
 * Caso de teste — Passo 4 do plano de execução.
 *
 * PROVA que o servidor que a nossa fábrica gera fala o MESMO protocolo que a
 * bancada espera. Sem isto, a tela trazida da referência mostra painéis vazios.
 *
 *   1. apresenta-se ao conectar, dizendo o que sabe fazer
 *   2. recusa tarefa antes de a rodada ser aberta
 *   3. abre a rodada quando pedido
 *   4. conta o que está fazendo, passo a passo, durante a tarefa
 *   5. consolida as etiquetas da tarefa ao terminar
 *   6. o envelope final tem os campos que a tela lê
 *   7. encerra a rodada quando pedido
 *
 * Uso:  node tests/execucao/prova-protocolo-servidor.mjs [porta]
 */
import WebSocket from 'ws';

const PORTA = process.argv[2] || 6401;
const res = [];
const confere = (nome, ok, det = '') => {
  res.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !det ? '' : '\n          ' + det}`);
};

const conversa = [];
const ws = new WebSocket(`ws://localhost:${PORTA}`);
const recebidas = () => conversa.map(m => m.type);
const primeira = (tipo) => conversa.find(m => m.type === tipo);
const esperaPor = (tipo, ms = 180000) => new Promise((ok) => {
  const t0 = Date.now();
  const iv = setInterval(() => {
    if (primeira(tipo) || Date.now() - t0 > ms) { clearInterval(iv); ok(primeira(tipo)); }
  }, 200);
});

ws.on('message', (m) => { try { conversa.push(JSON.parse(m.toString())); } catch {} });
await new Promise((ok, err) => { ws.on('open', ok); ws.on('error', err); });
await new Promise(r => setTimeout(r, 800));

const apresentacao = primeira('welcome');
confere('1. apresenta-se ao conectar, dizendo o que sabe fazer',
        !!apresentacao && Array.isArray(apresentacao.supported_tasks) && apresentacao.supported_tasks.length > 0,
        `recebido: ${JSON.stringify(recebidas())}`);

// tarefa ANTES de abrir a rodada — tem de ser recusada
ws.send(JSON.stringify({ type: 'execute_task', data: { task_name: 'tarefa_teste', input_data: {} } }));
await new Promise(r => setTimeout(r, 1200));
const recusa = conversa.find(m => m.type === 'error' && JSON.stringify(m).includes('iniciar_execucao'));
confere('2. recusa tarefa antes de a rodada ser aberta', !!recusa,
        `respostas ate agora: ${JSON.stringify(recebidas())}`);

ws.send(JSON.stringify({ type: 'iniciar_execucao', data: {} }));
const abriu = await esperaPor('execucao_iniciada', 10000);
confere('3. abre a rodada quando pedido', !!abriu && abriu.success === true);

const marcaPassos = conversa.length;
ws.send(JSON.stringify({ type: 'execute_task', data: { task_name: 'tarefa_teste', input_data: { pedido: 'prova' } } }));
const fim = await esperaPor('task_completed');

const passos = conversa.slice(marcaPassos).filter(m => m.type === 'execution_step');
confere('4. conta o que está fazendo, passo a passo, durante a tarefa',
        passos.length >= 2,
        `so ${passos.length} passo(s): ${JSON.stringify(passos.map(p => p.data?.step_type))}`);

const etiquetas = primeira('tags_extracted');
const NECESSARIAS = ['TASK_NAME','AGENT_NAME','TASK_INPUT','TOOL_INPUT','USED_TOOL','TASK_STEP',
                     'TASK_OUTPUT','TASK_OUTPUT_TYPE','AGENT_THOUGHT','TOOL_OUTPUT','TASK_COMPLETED'];
const faltando = etiquetas ? NECESSARIAS.filter(k => !(k in (etiquetas.tags || {}))) : NECESSARIAS;
confere('5. consolida as etiquetas da tarefa ao terminar',
        !!etiquetas && faltando.length === 0,
        `faltando: ${JSON.stringify(faltando)}`);

const envelope = fim?.data || {};
const CAMPOS = ['task_name','success','duration','universal_tags','result','timestamp'];
const semCampo = CAMPOS.filter(k => !(k in envelope));
confere('6. o envelope final tem os campos que a tela lê',
        !!fim && semCampo.length === 0,
        `faltando no envelope: ${JSON.stringify(semCampo)} | veio: ${JSON.stringify(Object.keys(envelope))}`);

ws.send(JSON.stringify({ type: 'finalizar_execucao', data: {} }));
const fechou = await esperaPor('execucao_finalizada', 10000);
confere('7. encerra a rodada quando pedido', !!fechou);

console.log(`\n  conversa completa: ${JSON.stringify(recebidas())}`);
ws.close();
const ok = res.filter(Boolean).length;
console.log(`\n  ${ok} de ${res.length} casos passaram, ${res.length - ok} falharam`);
process.exit(ok === res.length ? 0 : 1);
