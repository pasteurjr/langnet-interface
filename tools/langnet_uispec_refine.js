// Refina UMA tela da UI Spec pela interface. Uso: node langnet_uispec_refine.js "<nome da tela>" "<instrução>" <shotPrefix>
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep = ms => new Promise(r=>setTimeout(r,ms));
const screenName = process.argv[2], instruction = process.argv[3], prefix = process.argv[4] || 'uispec-fix';
(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:1050 } });
  let postFired=false, postDone=false, postStatus=0;
  p.on('request', r => { if (r.method()==='POST' && /(refine|chat)/.test(r.url())) { postFired=true; console.log('NET_POST:', r.url().split('/api/')[1]); } });
  p.on('response', r => { if (r.request().method()==='POST' && /(refine|chat)/.test(r.url())) { postDone=true; postStatus=r.status(); console.log('NET_RESP:', r.status()); } });
  await p.goto('http://localhost:3000',{ waitUntil:'domcontentloaded' });
  await p.evaluate(t=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOKEN);
  await p.goto(`http://localhost:3000/project/${PROJ}/ui-spec`,{ waitUntil:'networkidle' });
  await sleep(3500);
  // 1) seleciona a tela alvo na lista (clica no título exato da tela)
  const item = p.getByText(screenName, { exact: true }).first();
  await item.click();
  await sleep(1500);
  // 2) garante chat aberto
  const openChat = p.locator('button', { hasText: /Refinar com o agente/i }).first();
  if (await openChat.count()) { await openChat.click(); await sleep(1200); }
  // 3) textarea de refino da tela (placeholder = Refinar "<tela>") — VERIFICA a seleção
  const ta = p.locator('textarea[placeholder^="Refinar"]').first();
  const ph = await ta.getAttribute('placeholder');
  console.log('PLACEHOLDER_CHAT:', ph);
  if (!ph || ph.indexOf(screenName) < 0) { console.log('ERRO_SELECAO: chat não está na tela alvo ('+screenName+')'); await b.close(); process.exit(2); }
  console.log('TELA_SELECIONADA_OK:', screenName);
  if (process.env.DRYRUN) { await b.close(); console.log('DONE'); return; }
  await ta.click();
  await ta.pressSequentially(instruction, { delay: 3 });
  console.log('INSTRUCAO:', instruction);
  await p.screenshot({ path: `${OUT}/${prefix}-instrucao.png`, fullPage: true });
  // 4) botão "Refinar" (o de enviar, dentro do painel de chat — o último "Refinar")
  const send = p.locator('button', { hasText: /^Refinar$/ }).last();
  await send.click();
  await sleep(2500);
  if (!postFired) { console.log('  (Refinar não disparou POST — tentando Ctrl+Enter)'); await ta.press('Control+Enter'); await sleep(2500); }
  if (!postFired) { console.log('AVISO_SEND_FALHOU'); }
  console.log('▷ aguardando agente...');
  let done=false;
  for (let i=0;i<84;i++){ await sleep(5000); if (postDone){ console.log('POST fim status', postStatus); done=(postStatus>=200&&postStatus<300); break;} if (i%6===0) console.log('  ...',(i+1)*5,'s (fired='+postFired+')'); }
  await sleep(3000);
  await p.screenshot({ path: `${OUT}/${prefix}-depois.png`, fullPage: true });
  console.log(done ? 'REFINO_OK' : 'REFINO_FALHOU');
  await b.close(); console.log('DONE');
})().catch(e => { console.error('FALHOU:', e.message); process.exit(1); });
