// Redescobre as ferramentas do servidor MCP do BioByte pela página global de MCP ("Testar Conexão").
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '900', 10);
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO PÁGINA:',m.text().slice(0,200));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/mcp/config`,{waitUntil:'domcontentloaded'});
  await sleep(4000);
  // Botão "Testar Conexão" DO SERVIDOR BioByte: faz o handshake e regrava as ferramentas descobertas.
  await p.evaluate(()=>window.scrollTo(0, document.body.scrollHeight)); await sleep(800);
  await shot(p,'mcp-antes-teste');
  // o botão real da lista de servidores registrados é "🔌 Testar" (o 🔗 da tabela antiga é decorativo)
  const item = p.locator('*').filter({ hasText: /BioByte Sentinela - Integrações/ }).filter({ has: p.getByRole('button', { name: /🔌 Testar/ }) }).last();
  const btn = item.getByRole('button', { name: /🔌 Testar/ }).first();
  console.log('botão do BioByte encontrado:', await btn.count());
  await btn.click({timeout:15000});
  console.log('▷ teste do servidor BioByte disparado');
  await sleep(12000);
  const t = await p.evaluate(()=>document.body.innerText);
  const i0 = t.indexOf('BioByte'); console.log('BioByte na página:', i0>=0 ? t.slice(i0, i0+220).replace(/\n/g,' | ') : 'não achado');
  await shot(p,'mcp-depois-teste');
  await b.close();
  console.log('DONE mcp próximo índice', N);
})();
