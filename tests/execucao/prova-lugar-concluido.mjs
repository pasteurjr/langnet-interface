/**
 * Caso de teste — Passo 2 do plano de execução.
 *
 * PROVA a segunda condição de aptidão da rede temporizada:
 *   um token que está SENDO PROCESSADO é um token INDISPONÍVEL —
 *   ele existe na marcação, mas não habilita transição nenhuma
 *   enquanto o processo do lugar não terminar.
 *
 * Rede:  P1 -> T1 -> P2 -> T2 -> P3
 *        P2 tem lógica que demora.
 *
 * Uso:  node tests/execucao/prova-lugar-concluido.mjs
 */
import { PetriNetSimulator } from '../../src/components/petri-net/PetriNetSimulator.js';

const DEMORA = 1500;     // quanto a lógica do lugar leva
const rede = () => ({
  lugares: [
    { id: 'P1', nome: 'inicio',  tokens: 1, logica: '' },
    { id: 'P2', nome: 'demora',  tokens: 0, logica:
        `const output = utils.clone(input);
         await new Promise(r => setTimeout(r, ${DEMORA}));
         output.trabalho_feito = true;
         output.status = 'completed';
         return output;` },
    { id: 'P3', nome: 'fim',     tokens: 0, logica: '' }
  ],
  transicoes: [ { id: 'T1', nome: 'inicia' }, { id: 'T2', nome: 'avanca' } ],
  arcos: [
    { origem: 'P1', destino: 'T1' }, { origem: 'T1', destino: 'P2' },
    { origem: 'P2', destino: 'T2' }, { origem: 'T2', destino: 'P3' }
  ]
});

const espera = (ms) => new Promise(r => setTimeout(r, ms));
const resultados = [];
const confere = (nome, ok, detalhe = '') => {
  resultados.push(ok);
  console.log(`  ${ok ? 'passou' : 'FALHOU'}  ${nome}${ok || !detalhe ? '' : '\n          ' + detalhe}`);
};

const sim = new PetriNetSimulator(rede());

// --- T1 deve estar apta (P1 tem token e não tem lógica) ---
confere('1. transição inicial está apta (marcação satisfeita)',
        sim.isTransitionEnabled('T1') === true);

// --- dispara T1: token vai para P2, que começa a processar ---
sim.fireTransition('T1');
await espera(60);   // deixa o processamento arrancar

confere('2. o token chegou em P2 (marcação diz que sim)',
        (sim.markingVector['P2'] || 0) === 1,
        `P2 tem ${sim.markingVector['P2']} tokens`);

confere('3. o processador SABE que P2 está processando',
        sim.placeProcessor.isProcessing('P2') === true,
        'isProcessing("P2") devolveu false enquanto a lógica ainda roda');

// --- O CASO CENTRAL: T2 não pode estar apta agora ---
confere('4. T2 NÃO está apta enquanto P2 processa (token indisponível)',
        sim.isTransitionEnabled('T2') === false,
        'T2 ficou apta com o lugar anterior ainda rodando — a rede avança em cima de dado inexistente');

// --- espera o lugar terminar ---
await espera(DEMORA + 400);

confere('5. o processador reconhece que P2 terminou',
        sim.placeProcessor.isProcessing('P2') === false);

confere('6. P2 produziu resultado de verdade (não cópia da entrada)',
        sim.petriNet.lugares[1].output_data?.trabalho_feito === true,
        `saída de P2: ${JSON.stringify(sim.petriNet.lugares[1].output_data || {}).slice(0,100)}`);

confere('7. SÓ AGORA T2 fica apta',
        sim.isTransitionEnabled('T2') === true,
        'T2 continuou inapta depois de P2 concluir — a rede travou');

const ok = resultados.filter(Boolean).length;
console.log(`\n  ${ok} de ${resultados.length} casos passaram, ${resultados.length - ok} falharam`);
process.exit(ok === resultados.length ? 0 : 1);
