/**
 * Caso de teste — Passo 3 do plano de execução.
 *
 * PROVA que falha é falha: um lugar que não conseguiu fazer o que tinha de
 * fazer NÃO pode fingir que produziu, e NÃO pode liberar a transição seguinte.
 *
 *   1. lugar que falha não copia a entrada para a saída
 *   2. lugar que falha fica marcado como ERRO (não como concluído)
 *   3. lugar que falha guarda o motivo, legível
 *   4. a transição seguinte NÃO libera
 *   5. quem vai buscar o anterior distingue "produziu" de "falhou"
 *   6. controle: lugar que dá certo continua liberando normalmente
 *
 * Uso:  node tests/execucao/prova-falha-nao-passa.mjs
 */
import { PetriNetSimulator } from '../../src/components/petri-net/PetriNetSimulator.js';

const espera = (ms) => new Promise(r => setTimeout(r, ms));
const res = [];
const confere = (nome, ok, det = '') => {
  res.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !det ? '' : '\n          ' + det}`);
};

const rede = (logicaDoMeio) => ({
  lugares: [
    { id: 'P1', nome: 'inicio', tokens: 1, logica: '' },
    { id: 'P2', nome: 'tarefa', tokens: 0, logica: logicaDoMeio },
    { id: 'P3', nome: 'seguinte', tokens: 0, logica:
        `const output = utils.clone(input);
         const anterior = utils.getPlaceOutput('P2');
         output.viu_anterior = anterior;
         return output;` }
  ],
  transicoes: [{ id: 'T1', nome: 't1' }, { id: 'T2', nome: 't2' }],
  arcos: [
    { origem: 'P1', destino: 'T1' }, { origem: 'T1', destino: 'P2' },
    { origem: 'P2', destino: 'T2' }, { origem: 'T2', destino: 'P3' }
  ]
});

// ---------- o lugar do meio FALHA ----------
{
  const sim = new PetriNetSimulator(rede(
    `const output = utils.clone(input);
     await new Promise(r => setTimeout(r, 100));
     throw new Error('o servico externo recusou: faltam cc e bcc');`));
  sim.startSimulation();
  sim.fireTransition('T1');
  await espera(900);

  const p2 = sim.petriNet.lugares.find(l => l.id === 'P2');

  confere('1. lugar que falha NÃO copia a entrada para a saída',
          !(p2.output_data && p2.output_data.from_transition === 'T1' && !p2.output_data.error),
          `saída de P2: ${JSON.stringify(p2.output_data || {}).slice(0,140)} — parece que produziu, mas é só o que entrou`);

  confere('2. lugar que falha fica marcado como ERRO',
          p2.status === 'error',
          `estado ficou "${p2.status}"`);

  confere('3. o motivo da falha fica registrado e legível',
          typeof p2.error === 'string' && p2.error.includes('recusou'),
          `motivo guardado: ${JSON.stringify(p2.error)}`);

  confere('4. a transição seguinte NÃO libera',
          sim.isTransitionEnabled('T2') === false,
          'T2 liberou com o lugar anterior tendo FALHADO — a cadeia segue sobre lixo');

  // 5. quem busca o anterior tem como distinguir
  const visto = p2.output_data || {};
  const daParaDistinguir = visto.status === 'error' || !!visto.error || Object.keys(visto).length === 0;
  confere('5. quem vai buscar o anterior consegue distinguir "produziu" de "falhou"',
          daParaDistinguir,
          `o que o seguinte veria: ${JSON.stringify(visto).slice(0,140)}`);
}

// ---------- controle: o lugar do meio DÁ CERTO ----------
{
  const sim = new PetriNetSimulator(rede(
    `const output = utils.clone(input);
     await new Promise(r => setTimeout(r, 100));
     output.trabalho = 'feito'; return output;`));
  sim.startSimulation();
  sim.fireTransition('T1');
  await espera(900);
  const p2 = sim.petriNet.lugares.find(l => l.id === 'P2');
  confere('6. controle: lugar que dá certo continua concluindo e liberando',
          p2.status === 'completed' && p2.output_data?.trabalho === 'feito' && sim.isTransitionEnabled('T2') === true,
          `estado=${p2.status} saída=${JSON.stringify(p2.output_data||{}).slice(0,80)} apta=${sim.isTransitionEnabled('T2')}`);
}

const ok = res.filter(Boolean).length;
console.log(`\n  ${ok} de ${res.length} casos passaram, ${res.length - ok} falharam`);
process.exit(ok === res.length ? 0 : 1);
