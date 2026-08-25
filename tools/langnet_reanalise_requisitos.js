// Re-dispara a Análise de Requisitos PELA UI com instrução forte focando os parâmetros
// urbanísticos + zoneamento (os docs já estão no projeto). Gera nova versão dos requisitos.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/solo-v3-tutorial/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const INSTR = [
  "Gerar requisitos funcionais COMPLETOS e EQUILIBRADOS, cobrindo os TRES eixos SEM OMITIR nenhum:",
  "EIXO 1 (URBANISTICO) parametros por zona: coeficiente de aproveitamento, taxa de ocupacao, permeabilidade,",
  "recuos frontal/lateral/fundos, gabarito, area minima de lote, usos permitidos, e o ZONEAMENTO (poligonais).",
  "EIXO 2 (AMBIENTAL) APP e Codigo Florestal (faixas por curso dagua/nascente/lagoa), Reserva Legal, declividade.",
  "EIXO 3 (LICENCIAMENTO E LAUDO) classificacao e licenciamento Sisema/COPAM (classes 1-6, AAF/licenciamento) e",
  "EMISSAO DE LAUDO/PARECER de conformidade com estrutura completa. Cada parametro/regra DEVE virar um requisito",
  "verificavel (valor exigido pela zona x valor do projeto -> conforme/nao conforme), com fundamentacao legal."
].join(" ");
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  let fired = false, status = 0;
  p.on('response', r => { if (r.request().method() === 'POST' && /analyze-batch/.test(r.url())) { fired = true; status = r.status(); } });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/documents`, { waitUntil: 'networkidle' });
  await sleep(4500);
  // instrução de análise (forte)
  const instr = p.locator('textarea[placeholder^="Ex: Focar"]').first();
  if (!(await instr.count())) { console.log('ERRO: textarea de instrução não encontrada'); await b.close(); process.exit(2); }
  await instr.click();
  await instr.fill('');
  await instr.pressSequentially(INSTR, { delay: 1 });
  console.log('instrução definida (', INSTR.length, 'chars )');
  await p.screenshot({ path: `${OUT}/legis-04-reanalise-instrucao.png`, fullPage: true });
  // dispara
  const startBtn = p.locator('button.btn-start-analysis, button', { hasText: /Iniciar An[aá]lise/ }).first();
  await startBtn.click();
  console.log('▷ re-análise disparada; aguardando POST…');
  for (let i = 0; i < 24; i++) { await sleep(3000); if (fired) { console.log('analyze-batch status', status); break; } }
  await sleep(2000);
  console.log(fired ? 'REANALISE_INICIADA' : 'NAO_DISPAROU');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
