// Driver reutilizável da UI do LangNet (Playwright headless).
// Uso: node langnet_ui_driver.js <stage> <shotPrefix> ["instrução de refino"]
// stage: data-model | tasks | petri | code | spec | ui-spec | agent-task | test-cases
const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const BASE = 'http://localhost:3000';
const PROJ = '9cbea119-c57b-4df1-a183-2ff68b5040e1';
const TOKEN = fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/clinica-medica/langnet-ui-drive/shots';
const sleep = ms => new Promise(r=>setTimeout(r,ms));

const stage = process.argv[2] || 'data-model';
const prefix = process.argv[3] || stage;
const instruction = process.argv[4] || '';

function versionText(p){ return p.evaluate(()=>{
  const m = document.body.innerText.match(/Vers[aã]o\s*v?(\d+)/i); return m?m[1]:'?';
}); }
function validationText(p){ return p.evaluate(()=>{
  const m = document.body.innerText.match(/Valida[cç][aã]o[^\n]*/i); return m?m[0]:'(sem validação)';
}); }

(async () => {
  const b = await chromium.launch({ headless:true });
  const p = await b.newPage({ viewport:{ width:1500, height:950 } });
  p.on('dialog', d=>d.dismiss().catch(()=>{}));
  await p.goto(BASE, { waitUntil:'domcontentloaded' });
  await p.evaluate((t)=>{ localStorage.setItem('accessToken', t); localStorage.setItem('token', t); }, TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/${stage}`, { waitUntil:'networkidle' });
  await sleep(3500);
  const vBefore = await versionText(p);
  console.log('VERSAO_ANTES:', vBefore);
  console.log('VALIDACAO_ANTES:', await validationText(p));
  await p.screenshot({ path: `${OUT}/${prefix}-antes.png`, fullPage: true });
  console.log('📸', `${prefix}-antes`);

  if (instruction) {
    // detecção de rede: registra POST de refino/chat e sua resposta
    let postFired = false, postDone = false, postStatus = 0;
    p.on('request', r => { if (r.method()==='POST' && /\/(chat|refine)(\?|$)/.test(r.url())) { postFired = true; console.log('NET_POST_ENVIADO:', r.url().split('/api/')[1]||r.url()); } });
    p.on('response', async r => { if (r.request().method()==='POST' && /\/(chat|refine)(\?|$)/.test(r.url())) { postDone = true; postStatus = r.status(); console.log('NET_POST_RESPOSTA:', r.status()); } });

    const openChat = p.locator('button', { hasText: /Refinar com o agente/i }).first();
    if (await openChat.count()) { await openChat.click(); await sleep(1500); }
    let chatInput = p.locator('input[placeholder*="adicione"], input[placeholder*="Ex:"]').last();
    if (!(await chatInput.count())) chatInput = p.locator('textarea').last();
    await chatInput.click();
    await chatInput.press('Control+a'); await chatInput.press('Backspace');
    await chatInput.pressSequentially(instruction, { delay: 3 });   // digitação REAL (dispara onChange do React)
    console.log('INSTRUCAO_ENVIADA:', instruction);
    await p.screenshot({ path: `${OUT}/${prefix}-instrucao.png`, fullPage: true });

    const send = p.locator('button', { hasText: /^Enviar$/i }).first();
    if (await send.count()) await send.click();
    await sleep(2500);
    if (!postFired) { console.log('  (Enviar não disparou POST — tentando Enter)'); await chatInput.press('Enter'); await sleep(2500); }
    if (!postFired) { console.log('AVISO_SEND_FALHOU: nenhum POST disparado'); }
    console.log('▷ aguardando resposta do agente...');
    let done = false;
    for (let i=0;i<84;i++){          // até 7 min
      await sleep(5000);
      if (postDone) { console.log('POST concluído status', postStatus, 'em ~', (i+1)*5, 's'); done = (postStatus>=200 && postStatus<300); break; }
      const v = await versionText(p);
      if (v !== vBefore && v !== '?') { console.log('VERSAO_MUDOU para', v); done=true; break; }
      if (i%6===0) console.log('  ...', (i+1)*5, 's (postFired='+postFired+')');
    }
    await sleep(3000);
    console.log('VERSAO_DEPOIS:', await versionText(p));
    console.log('VALIDACAO_DEPOIS:', await validationText(p));
    await p.screenshot({ path: `${OUT}/${prefix}-depois.png`, fullPage: true });
    console.log('📸', `${prefix}-depois`);
    console.log(done ? 'REFINO_OK' : 'REFINO_FALHOU');
  }
  await b.close(); console.log('DONE');
})().catch(e=>{ console.error('FALHOU:', e.message); process.exit(1); });
