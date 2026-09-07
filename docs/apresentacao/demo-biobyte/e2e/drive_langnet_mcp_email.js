// Registra o servidor MCP de e-mail do BioByte pela interface, testa (descoberta), habilita no
// projeto e atribui a ferramenta enviar_email ao agente detector de MDR.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '900', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const NOME='BioByte Sentinela - Notificações (E-mail)';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
const campo=(p,rotulo)=>p.locator('div').filter({has:p.locator(`label:text-is("${rotulo}")`)}).locator('input, select').first();
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  p.on('dialog', d => d.accept().catch(()=>{}));
  p.on('console',m=>{if(m.type()==='error' && !/same key/.test(m.text()))console.log('ERRO PÁGINA:',m.text().slice(0,160));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/mcp/config`,{waitUntil:'domcontentloaded'}); await sleep(4000);
  const jaExiste = (await p.evaluate(()=>document.body.innerText)).includes(NOME);
  if (!jaExiste) {
    // campos identificados pelo placeholder (os rótulos não estão ligados aos campos)
    await p.getByPlaceholder('CRM da empresa').fill(NOME, {timeout:10000});
    await p.getByPlaceholder('crm, email, dados…').fill('communication', {timeout:10000});
    await p.getByPlaceholder('http://host:porta/sse').fill('http://127.0.0.1:9121/sse', {timeout:10000});
    await p.getByPlaceholder('CRM da empresa').scrollIntoViewIfNeeded();
    await shot(p,'mcp-email-formulario');
    await p.getByRole('button',{name:/💾 Registrar/}).click({timeout:15000});
    console.log('▷ servidor registrado'); await sleep(4000);
  } else console.log('servidor já registrado');
  // testar (descoberta) no cartão do servidor de e-mail
  await p.evaluate(()=>window.scrollTo(0, document.body.scrollHeight)); await sleep(800);
  const item = p.locator('*').filter({ hasText: new RegExp(NOME.replace(/[()]/g,'\\$&')) }).filter({ has: p.getByRole('button',{name:/🔌 Testar/}) }).last();
  await item.getByRole('button',{name:/🔌 Testar/}).first().click({timeout:15000});
  console.log('▷ teste/descoberta disparado'); await sleep(10000);
  const t = await p.evaluate(()=>document.body.innerText); const i0 = t.indexOf(NOME);
  console.log('cartão:', t.slice(i0, i0+240).replace(/\n/g,' | '));
  await shot(p,'mcp-email-descoberto');
  // projeto: habilitar + atribuir ao agente detector de MDR
  await p.goto(`${BASE}/project/${PROJ}/mcp`,{waitUntil:'domcontentloaded'}); await sleep(5000);
  const linha = p.locator('div').filter({ has: p.locator(`b:text-is("${NOME}")`) }).filter({ has: p.getByRole('button',{name:/habilitar|habilitado/}) }).last();
  const btnHab = linha.getByRole('button',{name:/habilitar|habilitado/}).first();
  const txtHab = (await btnHab.innerText().catch(()=>'')).trim();
  if (/^habilitar$/i.test(txtHab)) { await btnHab.click(); console.log('▷ habilitado no projeto'); await sleep(3000); } else console.log('servidor no projeto:', txtHab || 'não achado');
  await shot(p,'mcp-email-projeto-habilitado');
  const bloco = p.locator('div').filter({ has: p.locator('div:text-is("mdr_detector_agent")') }).filter({ has: p.locator('select') }).last();
  const sel = bloco.locator('select').first();
  const opcoes = await sel.locator('option').allTextContents(); console.log('opções do agente:', opcoes.filter(o=>/enviar_email/.test(o)));
  const alvo = (await sel.locator('option').evaluateAll(os=>os.map(o=>[o.value,o.textContent]))).find(([v,tx])=>/enviar_email/.test(tx||''));
  if (alvo) { await sel.selectOption(alvo[0]); await bloco.getByRole('button',{name:'+'}).first().click(); console.log('▷ enviar_email atribuída a mdr_detector_agent'); await sleep(3000); }
  else console.log('enviar_email não apareceu nas opções');
  await shot(p,'mcp-email-atribuido');
  await b.close(); console.log('DONE próximo índice', N);
})();
