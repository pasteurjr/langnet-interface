// Fotografa as OPÇÕES de framework, protocolo e modelo na tela de criação de projeto.
// Um seletor nativo abre uma janelinha do sistema, que não entra em captura de tela; por isso
// as opções são expandidas na própria página (atributo `size`) — são as MESMAS opções reais do
// formulário, só desenhadas em lista. Nada é inventado nem acrescentado.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '900', 10);
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1100}});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`${BASE}/projects`,{waitUntil:'domcontentloaded'}); await sleep(6000);
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button,a')].find(e=>/novo projeto|criar projeto/i.test(e.textContent||'')); if(b)b.click();});
  await sleep(3000);
  const inventario = await p.evaluate(()=>{
    const out=[];
    for (const s of document.querySelectorAll('select')) {
      const rot=((s.closest('div')?.textContent)||'').split('\n')[0].trim().slice(0,40);
      out.push({rotulo:rot, opcoes:[...s.options].map(o=>o.textContent.trim())});
      s.setAttribute('size', String(Math.min(s.options.length, 10)));
      s.style.height='auto';
    }
    return out;
  });
  console.log(JSON.stringify(inventario,null,1));
  await sleep(700);
  await shot(p,'opcoes-framework-protocolo-modelo');
  await b.close();
})();
