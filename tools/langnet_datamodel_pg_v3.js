// Dirige a UI do LangNet: Modelo de Dados -> seleciona PostgreSQL + spec -> Regenerar do zero.
// Prova que o produto gera schema PostGIS PELA INTERFACE. Uso: node langnet_datamodel_pg.js
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt', 'utf8').trim();
const PROJ = 'c4871aaf-3c8c-41d3-8ca7-6c3e22189731';       // v3 (cascata unificada)
const SPEC = '573139a3';                                     // spec do v3 <- requisitos v4 unificados (dc66b1e7)
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/uso-do-solo/cascata-completa/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1500, height: 1200 } });
  let genFired = false, genDone = false, genStatus = 0;
  p.on('request', r => { if (r.method() === 'POST' && /data-model\/.*\/generate/.test(r.url())) { genFired = true; console.log('NET_POST generate'); } });
  p.on('response', async r => { if (r.request().method() === 'POST' && /data-model\/.*\/generate/.test(r.url())) { genDone = true; genStatus = r.status(); console.log('NET_RESP', r.status()); if (r.status() >= 400) { try { console.log('  ERR_BODY:', (await r.text()).slice(0, 300)); } catch (e) {} } } });
  await p.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
  await p.evaluate(t => { localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  let navok=false;
  for(let a=1;a<=4&&!navok;a++){ await p.goto(`http://localhost:3000/project/${PROJ}/data-model`,{waitUntil:'domcontentloaded'}).catch(()=>{}); navok=await p.locator('select:has(option[value="postgresql"])').first().waitFor({timeout:40000}).then(()=>true).catch(()=>false); console.log('nav dm #'+a,navok); }
  if(!navok){console.log('ERRO: pagina data-model nao carregou');await b.close();process.exit(3);}
  await sleep(2000);

  // 1) seleciona a Especificação de origem (a de 65KB)
  const specSel = p.locator('select[title="Especificação de origem"]').first();
  if (await specSel.count()) {
    const opts = await specSel.locator('option').all();
    for (const o of opts) { const v = await o.getAttribute('value'); if (v && v.startsWith(SPEC)) { await specSel.selectOption(v); console.log('SPEC selecionada:', v.slice(0,8)); break; } }
  } else { console.log('AVISO: select de spec não encontrado'); }
  await sleep(800);

  // 2) seleciona DBMS = PostgreSQL
  const dbmsSel = p.locator('select:has(option[value="postgresql"])').first();
  if (!(await dbmsSel.count())) { console.log('ERRO: seletor DBMS não encontrado'); await b.close(); process.exit(2); }
  await dbmsSel.selectOption('postgresql');
  console.log('DBMS selecionado: postgresql');
  await sleep(600);
  await p.screenshot({ path: `${OUT}/18-dm-antes.png`, fullPage: true });

  // 3) clica em Gerar/Regenerar
  const genBtn = p.locator('button', { hasText: /Regenerar do zero|Gerar Modelo de Dados/ }).first();
  if (!(await genBtn.count())) { console.log('ERRO: botão gerar não encontrado'); await b.close(); process.exit(3); }
  await genBtn.click();
  console.log('▷ clicou em gerar; aguardando LLM (extract+normalize+ddl+validate)…');
  await sleep(2500);
  if (!genFired) { console.log('AVISO: POST generate não disparou (falta spec?)'); }

  // 4) aguarda a resposta (LLM pode demorar; até ~12 min)
  let done = false;
  for (let i = 0; i < 300; i++) {
    await sleep(5000);
    if (genDone) { console.log('generate resp status', genStatus); done = (genStatus >= 200 && genStatus < 300); break; }
    if (i % 6 === 0) console.log('  …', (i + 1) * 5, 's (fired=' + genFired + ')');
  }
  await sleep(3000);

  // 5) captura resultado + abre aba Schema SQL
  await p.screenshot({ path: `${OUT}/19-dm-resultado.png`, fullPage: true });
  const sqlTab = p.locator('button.dm-tab', { hasText: /Schema SQL/ }).first();
  if (await sqlTab.count()) { await sqlTab.click(); await sleep(1500); }
  await p.screenshot({ path: `${OUT}/20-dm-schema-sql.png`, fullPage: true });

  const txt = await p.evaluate(() => document.body.innerText);
  console.log('DBMS badge:', (txt.match(/DBMS\s+\w+/i) || ['(n/a)'])[0]);
  console.log('Validação:', (txt.match(/Valida[cç][aã]o[^\n]*/i) || ['(n/a)'])[0]);
  ['CREATE EXTENSION', 'geometry(', 'gen_random_uuid', 'USING GIST', 'postgis'].forEach(k =>
    console.log('  schema contém', JSON.stringify(k) + ':', txt.includes(k)));
  console.log(done ? 'GERACAO_OK' : 'GERACAO_INCOMPLETA');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
