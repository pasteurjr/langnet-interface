// Etapa 1 — Documentos: anexa a ata de levantamento e captura cada momento.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '5', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const DOC='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/seed/levantamento_requisitos_biobyte.txt';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(7000);
  await shot(p,'etapa-documentos-vazia');
  // O campo de arquivo fica escondido atras do botao "Fazer Upload": e preciso acionar o botao e
  // pegar o seletor de arquivo que o navegador abre.
  const escolha = p.waitForEvent('filechooser', { timeout: 20000 });
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button')].find(e=>/fazer upload|\+ *upload/i.test(e.textContent||'')); if(b)b.click();});
  const fc = await escolha.catch(()=>null);
  if (fc) { await fc.setFiles(DOC); }
  else {
    const inp = p.locator('input[type=file]').first();
    if (!await inp.count()) { console.log('!! nao consegui anexar'); await b.close(); return; }
    await inp.setInputFiles(DOC);
  }
  console.log('documento anexado:', DOC.split('/').pop());
  await sleep(3000);
  await shot(p,'documento-anexado');
  // O botao que confirma e o VERDE dentro da janela ("Upload"), nao o "+ Upload" da barra.
  const enviar = p.getByRole('button', { name: /^\s*📤?\s*Upload\s*$/ }).last();
  if (await enviar.count()) {
    await enviar.click({ timeout: 20000, force: true }).catch(e=>console.log('clique:', String(e.message).split('\n')[0]));
    console.log('confirmado o envio');
  } else { console.log('!! botao de confirmar nao achado'); }
  await sleep(8000);
  await shot(p,'documento-carregado');
  console.log('texto da página:', (await p.evaluate(()=>document.body.innerText)).replace(/\n+/g,' | ').slice(200,520));
  await b.close();
})();
