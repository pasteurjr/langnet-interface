// Enriquece o Modelo de Dados PELA UI (chat "Refinar") com os campos de conformidade de
// uso do solo + entidade laudo. Prova que o LangNet complementa o modelo pela interface.
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'a1391183-f348-4a78-8773-8046b90a7676';   // tem a sessão PostGIS 935496ca como latest
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/solo-v3-tutorial/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const INSTRUCAO = [
  "Enriqueca o modelo para conformidade de uso do solo:",
  "1) na tabela requisito_gerado adicione as colunas: tipo (ENUM: urbanistico, ambiental, documental),",
  "fundamentacao_legal (VARCHAR 255), parametro (VARCHAR 100), valor_exigido (VARCHAR 255),",
  "valor_projeto (VARCHAR 255), situacao (ENUM: conforme, nao_conforme, pendente).",
  "2) na tabela regra_aplicavel adicione: tipo (ENUM: urbanistico, ambiental, documental),",
  "fundamentacao_legal (VARCHAR 255), parametro (VARCHAR 100), valor_exigido (VARCHAR 255).",
  "3) crie a tabela laudo com: id (UUID PK), consulta_id (UUID, FK para consulta),",
  "conclusao (ENUM: viavel, condicionado, inviavel), responsavel_tecnico (VARCHAR 255),",
  "art (VARCHAR 100), documento (TEXT), data_emissao (DATE).",
  "Mantenha todas as tabelas e colunas ja existentes."
].join(" ");
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  let fired = false, done = false, status = 0;
  p.on('request', r => { if (r.method() === 'POST' && /data-model\/.*\/chat/.test(r.url())) { fired = true; console.log('NET_POST chat'); } });
  p.on('response', r => { if (r.request().method() === 'POST' && /data-model\/.*\/chat/.test(r.url())) { done = true; status = r.status(); console.log('NET_RESP', r.status()); } });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/data-model`, { waitUntil: 'networkidle' });
  await sleep(9000);
  // confirma que carregou a sessão PostGIS
  const txt0 = await p.evaluate(() => document.body.innerText);
  console.log('DBMS carregado:', (txt0.match(/DBMS\s+\w+/i) || ['(n/a)'])[0]);
  // o chat começa COLAPSADO — clica em "Refinar com o agente" para expandir
  const toggle = p.locator('button', { hasText: /Refinar com o agente/ }).first();
  if (await toggle.count()) { await toggle.click(); console.log('chat expandido'); await sleep(1200); }
  // chat input (aceita input/textarea; fallback: qualquer placeholder com 'adicione' ou 'refinar')
  let chat = p.locator('input[placeholder^="Ex: adicione"], textarea[placeholder^="Ex: adicione"]').first();
  if (!(await chat.count())) chat = p.locator('input[placeholder*="dicione"], textarea[placeholder*="dicione"], input[placeholder*="efinar"], textarea[placeholder*="efinar"]').first();
  if (!(await chat.count())) {
    console.log('ERRO: input do chat não encontrado. Snippet da página:');
    console.log(txt0.slice(0, 500).replace(/\n+/g, ' | '));
    const phs = await p.$$eval('input,textarea', els => els.map(e => e.placeholder).filter(Boolean));
    console.log('placeholders na página:', JSON.stringify(phs));
    await p.screenshot({ path: `${OUT}/solo-pg-enrich-debug.png`, fullPage: true });
    await b.close(); process.exit(2);
  }
  await chat.click();
  await chat.pressSequentially(INSTRUCAO, { delay: 1 });
  console.log('INSTRUCAO digitada (', INSTRUCAO.length, 'chars )');
  await p.screenshot({ path: `${OUT}/solo-pg-enrich-01-instrucao.png`, fullPage: true });
  // botão Enviar
  const send = p.locator('button', { hasText: /^Enviar$/ }).first();
  await send.click();
  await sleep(2500);
  if (!fired) { console.log('AVISO: POST chat não disparou'); }
  console.log('▷ aguardando refino do modelo (LLM)…');
  for (let i = 0; i < 170; i++) { await sleep(5000); if (done) { console.log('chat resp', status); break; } if (i % 6 === 0) console.log('  …', (i + 1) * 5, 's'); }
  await sleep(4000);
  await p.screenshot({ path: `${OUT}/solo-pg-enrich-02-resultado.png`, fullPage: true });
  // abre Schema SQL e verifica
  const sqlTab = p.locator('button.dm-tab', { hasText: /Schema SQL/ }).first();
  if (await sqlTab.count()) { await sqlTab.click(); await sleep(1500); }
  await p.screenshot({ path: `${OUT}/solo-pg-enrich-03-schema.png`, fullPage: true });
  const txt = await p.evaluate(() => document.body.innerText);
  ['laudo', 'fundamentacao_legal', 'valor_exigido', 'situacao', 'responsavel_tecnico', 'conclusao'].forEach(k =>
    console.log('  schema contém', JSON.stringify(k) + ':', txt.includes(k)));
  console.log((status >= 200 && status < 300) ? 'REFINO_OK' : 'REFINO_INCOMPLETO');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
