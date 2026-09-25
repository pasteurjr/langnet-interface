/**
 * Verificação cética dos passos 1 e 2 — casos que os testes anteriores NÃO cobriram.
 *
 *  A. lugar que já NASCE com token e TEM lógica  (marcação inicial)
 *  B. lugar sem lógica não pode travar a rede
 *  C. JUNÇÃO: dois lugares alimentando a mesma transição
 *  D. o disparo continua consumindo e produzindo token corretamente
 *
 * Uso:  node tests/execucao/prova-arestas-aptidao.mjs
 */
import { PetriNetSimulator } from '../../src/components/petri-net/PetriNetSimulator.js';

const espera = (ms) => new Promise(r => setTimeout(r, ms));
const r = [];
const confere = (nome, ok, det = '') => {
  r.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !det ? '' : '\n          ' + det}`);
};
const demora = (ms, marca) =>
  `const output = utils.clone(input);
   await new Promise(x => setTimeout(x, ${ms}));
   output.${marca} = true; return output;`;

// ---------- A. lugar que nasce com token E tem lógica ----------
{
  const sim = new PetriNetSimulator({
    lugares: [
      { id: 'A1', nome: 'nasce com token e tem logica', tokens: 1, logica: demora(800, 'fez') },
      { id: 'A2', nome: 'depois', tokens: 0, logica: '' }
    ],
    transicoes: [{ id: 'TA', nome: 'ta' }],
    arcos: [{ origem: 'A1', destino: 'TA' }, { origem: 'TA', destino: 'A2' }]
  });
  const aptaAntes = sim.isTransitionEnabled('TA');
  confere('A1. lugar que nasce com token e tem lógica: transição bloqueada antes de rodar',
          aptaAntes === false,
          'a transição ficou apta sem a lógica ter rodado — o trabalho do lugar é PULADO');

  sim.startSimulation();                      // é quem dispara o trabalho da marcação inicial
  await espera(120);
  confere('A2. ao iniciar, o lugar da marcação inicial começa a trabalhar',
          sim.placeProcessor.isProcessing('A1') === true,
          'ninguém executou o lugar que nasceu com token — a rede travaria para sempre');

  await espera(1000);
  confere('A3. depois de concluir, o lugar produziu e a transição libera',
          sim.petriNet.lugares[0].output_data?.fez === true && sim.isTransitionEnabled('TA') === true,
          `produziu=${sim.petriNet.lugares[0].output_data?.fez} apta=${sim.isTransitionEnabled('TA')}`);
}

// ---------- B. lugar sem lógica não pode travar ----------
{
  const sim = new PetriNetSimulator({
    lugares: [ { id: 'B1', nome: 'sem logica', tokens: 1, logica: '' },
               { id: 'B2', nome: 'fim', tokens: 0, logica: '' } ],
    transicoes: [{ id: 'TB', nome: 'tb' }],
    arcos: [{ origem: 'B1', destino: 'TB' }, { origem: 'TB', destino: 'B2' }]
  });
  confere('B. lugar sem lógica está sempre pronto (não trava a rede)',
          sim.isTransitionEnabled('TB') === true,
          'a transição ficou inapta com um lugar que não tem nada a executar — a rede travaria');
}

// ---------- C. JUNÇÃO: dois lugares alimentam a mesma transição ----------
{
  const sim = new PetriNetSimulator({
    lugares: [
      { id: 'C0', nome: 'origem',  tokens: 1, logica: '' },
      { id: 'CA', nome: 'rapido',  tokens: 0, logica: demora(300,  'a_ok') },
      { id: 'CB', nome: 'lento',   tokens: 0, logica: demora(1800, 'b_ok') },
      { id: 'CF', nome: 'junta',   tokens: 0, logica: '' }
    ],
    transicoes: [{ id: 'TS', nome: 'separa' }, { id: 'TJ', nome: 'junta' }],
    arcos: [
      { origem: 'C0', destino: 'TS' }, { origem: 'TS', destino: 'CA' }, { origem: 'TS', destino: 'CB' },
      { origem: 'CA', destino: 'TJ' }, { origem: 'CB', destino: 'TJ' }, { origem: 'TJ', destino: 'CF' }
    ]
  });
  sim.fireTransition('TS');
  await espera(80);
  confere('C1. junção inapta com os DOIS lugares rodando', sim.isTransitionEnabled('TJ') === false);
  await espera(700);   // o rápido terminou, o lento não
  const aOk = sim.petriNet.lugares.find(l => l.id === 'CA').output_data?.a_ok === true;
  confere('C2. o lugar rápido concluiu', aOk);
  confere('C3. junção AINDA inapta — um dos lados continua rodando',
          sim.isTransitionEnabled('TJ') === false,
          'a junção liberou com um dos lados ainda trabalhando — o dado do lado lento não existe');
  await espera(1600);
  confere('C4. junção libera quando AMBOS concluem', sim.isTransitionEnabled('TJ') === true);
}

// ---------- D. o disparo continua correto (regressão do clássico) ----------
{
  const sim = new PetriNetSimulator({
    lugares: [ { id: 'D1', nome: 'a', tokens: 2, logica: '' }, { id: 'D2', nome: 'b', tokens: 0, logica: '' } ],
    transicoes: [{ id: 'TD', nome: 'td' }],
    arcos: [{ origem: 'D1', destino: 'TD', peso: 2 }, { origem: 'TD', destino: 'D2' }]
  });
  const apta = sim.isTransitionEnabled('TD');
  sim.fireTransition('TD');
  confere('D. disparo consome o peso do arco e produz na saída',
          apta === true && sim.markingVector['D1'] === 0 && sim.markingVector['D2'] === 1,
          `apta=${apta} D1=${sim.markingVector['D1']} D2=${sim.markingVector['D2']}`);
}


// ---------- E. transição SEM lugar de entrada (transição-fonte) ----------
{
  const sim = new PetriNetSimulator({
    lugares: [ { id: 'E1', nome: 'so saida', tokens: 0, logica: '' } ],
    transicoes: [{ id: 'TE', nome: 'fonte' }],
    arcos: [ { origem: 'TE', destino: 'E1' } ]     // nenhum arco CHEGA em TE
  });
  const apta = sim.isTransitionEnabled('TE');
  sim.fireTransition('TE');
  confere('E. transição sem lugar de entrada dispara sempre (fonte)',
          apta === true && sim.markingVector['E1'] === 1,
          `apta=${apta} E1=${sim.markingVector['E1']} — uma transição-fonte não pode ficar bloqueada`);
}

// ---------- F. o lugar SEGUINTE busca a saída do anterior (é assim que o dado anda) ----------
// O motor NÃO carrega o dado entre lugares — por desenho. Cada lugar vai buscar
// a saída do anterior com utils.getPlaceOutput, como a nossa fábrica emite.
{
  const sim = new PetriNetSimulator({
    lugares: [
      { id: 'F1', nome: 'inicia e produz', tokens: 1, logica:
          `return { execution_id: 'exec_123', system_initialized: true };` },
      { id: 'F2', nome: 'busca o anterior', tokens: 0, logica:
          `const output = utils.clone(input);
           const limite = Date.now() + 3000;
           let anterior = utils.getPlaceOutput('F1');
           while (!anterior.execution_id && Date.now() < limite) {
             await new Promise(x => setTimeout(x, 50));
             anterior = utils.getPlaceOutput('F1');
           }
           Object.assign(output, anterior);
           output.status = 'completed';
           return output;` }
    ],
    transicoes: [{ id: 'TF', nome: 'tf' }],
    arcos: [ { origem: 'F1', destino: 'TF' }, { origem: 'TF', destino: 'F2' } ]
  });
  sim.startSimulation();
  await espera(200);
  const produziu = sim.petriNet.lugares[0].output_data?.execution_id === 'exec_123';
  confere('F1. o lugar da marcação inicial produziu', produziu);

  sim.fireTransition('TF');
  await espera(600);
  const chegou = sim.petriNet.lugares[1].output_data?.execution_id === 'exec_123';
  confere('F2. o lugar seguinte BUSCOU e recebeu a saída do anterior',
          chegou,
          `saída de F2: ${JSON.stringify(sim.petriNet.lugares[1].output_data || {}).slice(0,140)}`);
}

const ok = r.filter(Boolean).length;
console.log(`\n  ${ok} de ${r.length} casos passaram, ${r.length - ok} falharam`);
process.exit(ok === r.length ? 0 : 1);
