// Sobe os 4 documentos de legislação PELA UI (etapa Documentos) e dispara a Análise ->
// nova versão dos requisitos, complementando a entrevista existente. Projeto: uso do solo.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';
const DIR = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/legislacao-fonte';
const FILES = [
  `${DIR}/01-restricoes-ambientais-APP-codigo-florestal.md`,
  `${DIR}/02-parametros-urbanisticos-uso-do-solo.md`,
  `${DIR}/03-licenciamento-ambiental-sisema-classes.md`,
  `${DIR}/04-estrutura-laudo-parecer-tecnico.md`,
];
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/solo-v3-tutorial/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  let upFired = 0, analyzeFired = false, analyzeStatus = 0;
  p.on('response', r => {
    const u = r.url();
    if (r.request().method() === 'POST' && /documents\/upload/.test(u)) upFired++;
    if (r.request().method() === 'POST' && /analyze-batch/.test(u)) { analyzeFired = true; analyzeStatus = r.status(); }
  });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/documents`, { waitUntil: 'networkidle' });
  await sleep(4000);

  // 1) abre modal de upload
  const upBtn = p.locator('button', { hasText: /Upload/i }).first();
  await upBtn.click(); await sleep(1200);
  // 2) seleciona os 4 arquivos
  const fileInput = p.locator('input[type="file"]').first();
  await fileInput.setInputFiles(FILES);
  console.log('arquivos selecionados:', FILES.length);
  await sleep(1000);
  await p.screenshot({ path: `${OUT}/legis-01-upload-modal.png`, fullPage: true });
  // 3) confirma upload (📤 Upload dentro do modal)
  const confirm = p.locator('button.btn-upload', { hasText: /Upload/ }).first();
  await confirm.click();
  console.log('▷ enviando upload…');
  for (let i = 0; i < 24; i++) { await sleep(2500); if (upFired >= 4) break; }
  console.log('uploads confirmados (POST /upload):', upFired);
  await sleep(2500);
  await p.screenshot({ path: `${OUT}/legis-02-docs-lista.png`, fullPage: true });

  // 4) instrução de análise
  const instr = p.locator('textarea[placeholder^="Ex: Focar"]').first();
  if (await instr.count()) {
    await instr.click();
    await instr.pressSequentially('Incorporar aos requisitos a legislacao de uso do solo: restricoes ambientais e APP (Codigo Florestal), parametros urbanisticos por zona, classificacao e licenciamento ambiental (Sisema/COPAM) e a emissao de laudo/parecer de conformidade.', { delay: 1 });
  }
  // (web research fica OFF)
  // 5) dispara a análise
  const startBtn = p.locator('button.btn-start-analysis, button', { hasText: /Iniciar An[aá]lise/ }).first();
  await startBtn.click();
  console.log('▷ análise disparada; aguardando confirmação do POST…');
  for (let i = 0; i < 20; i++) { await sleep(3000); if (analyzeFired) { console.log('analyze-batch status', analyzeStatus); break; } }
  await sleep(2000);
  await p.screenshot({ path: `${OUT}/legis-03-analise-iniciada.png`, fullPage: true });
  console.log(analyzeFired ? 'ANALISE_INICIADA' : 'ANALISE_NAO_DISPAROU');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
