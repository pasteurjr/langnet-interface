// Dispara a geração da ESPECIFICAÇÃO pela UI, a partir da nova versão de requisitos
// (sessão 01d24064 v1 — uso do solo com legislação incorporada). Cascade traçável.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';
const REQ_SESSION = '01d24064-f7c0-49d8-9eab-f20a89048685';
const REQ_VERSION = '1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/solo-v3-tutorial/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const INSTR = [
  "OBRIGATORIO: gere TODAS as 14 secoes numeradas (1 a 14), SEM PARAR antes da secao 14. Inclua",
  "explicitamente: 9. Fluxos de Trabalho, 10. Analise de Arquitetura, 11. Controle de Qualidade,",
  "12. Glossario, 13. Rastreabilidade (matriz FR/UC/BR), 14. Apendices. Seja CONCISO nos wireframes",
  "(no maximo 1 wireframe compacto por caso de uso) para ter orcamento de tokens para as 14 secoes.",
  "Conteudo COMPLETO e EQUILIBRADO cobrindo os TRES eixos do dominio (uso do solo):",
  "(1) URBANISTICO: parametros por zona (CA, TO, permeabilidade, recuos, gabarito, area minima, usos) e ZONEAMENTO poligonal;",
  "(2) AMBIENTAL: APP/Codigo Florestal (faixas por curso dagua/nascente/lagoa), Reserva Legal, declividade;",
  "(3) LICENCIAMENTO E LAUDO: classificacao Sisema/COPAM (classes) e EMISSAO DE LAUDO/PARECER de conformidade.",
  "Para cada regra, a tela/UC confronta valor exigido pela zona x valor do projeto -> conforme/nao conforme,",
  "com fundamentacao legal. Modelo de dados com entidades geoespaciais (zona, lote, poligonais, geometria) e o laudo."
].join(" ");

(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  let genFired = false, genStatus = 0, genBody = '';
  p.on('response', async r => {
    const u = r.url();
    if (r.request().method() === 'POST' && /\/specifications\/?$/.test(u)) {
      genFired = true; genStatus = r.status();
      try { genBody = JSON.stringify(await r.json()).slice(0, 200); } catch (e) {}
    }
  });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/specification`, { waitUntil: 'networkidle' });
  await sleep(4000);

  // 1) abre modal de seleção de requisitos (card-based: sessão -> versão -> preview)
  const reqBtn = p.locator('button.btn-requirements-compact').first();
  if (!(await reqBtn.count())) { console.log('ERRO: botão Requisitos não encontrado'); await b.close(); process.exit(2); }
  await reqBtn.click(); await sleep(3000);
  await p.screenshot({ path: `${OUT}/spec-01-modal-selecao.png`, fullPage: true });

  // 2) clica no PRIMEIRO card de sessão (mais recente = nossa 01d24064, 23:01)
  await p.locator('.session-item').first().click(); await sleep(2500);
  await p.screenshot({ path: `${OUT}/spec-01b-versoes.png`, fullPage: true });
  // 3) clica na versão (v1 = primeiro card na lista de versões)
  await p.locator('.session-item').first().click(); await sleep(2500);
  await p.screenshot({ path: `${OUT}/spec-01c-preview.png`, fullPage: true });
  // 4) confirma seleção (botão no preview)
  const confirmBtn = p.locator('button.btn-select', { hasText: /Selecionar este/ }).first();
  if (!(await confirmBtn.count())) { console.log('ERRO: botão Selecionar este Documento não encontrado'); await b.close(); process.exit(2); }
  await confirmBtn.click(); await sleep(2000);
  console.log('seleção confirmada (sessão mais recente v1)');
  await p.screenshot({ path: `${OUT}/spec-02-requisitos-selecionados.png`, fullPage: true });

  // 4) instrução customizada (textarea de instruções de análise, se existir)
  const instr = p.locator('textarea').first();
  if (await instr.count()) {
    try { await instr.click(); await instr.fill(''); await instr.pressSequentially(INSTR, { delay: 1 });
      console.log('instrução definida (', INSTR.length, 'chars )'); } catch (e) { console.log('sem textarea de instrução:', e.message); }
  }

  // 5) dispara a geração
  const startBtn = p.locator('button.btn-start-analysis').first();
  if (await startBtn.isDisabled()) { console.log('ERRO: botão Gerar ainda desabilitado (seleção não pegou)'); await p.screenshot({ path: `${OUT}/spec-ERRO.png`, fullPage: true }); await b.close(); process.exit(3); }
  await startBtn.click();
  console.log('▷ geração de especificação disparada; aguardando POST /specifications…');
  for (let i = 0; i < 24; i++) { await sleep(3000); if (genFired) break; }
  await sleep(1500);
  console.log('POST status:', genStatus, '| body:', genBody);
  await p.screenshot({ path: `${OUT}/spec-03-geracao-iniciada.png`, fullPage: true });
  console.log(genFired ? 'SPEC_INICIADA' : 'SPEC_NAO_DISPAROU');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
