// Refino da Especificação pela conversa, com captura.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '164', 10);
const PEDIDO = process.argv[3] || '';
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,100));});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/spec`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  // A "Comparação de Alterações" de um refino anterior abre sozinha e cobre a tela inteira —
  // a caixa de texto e o botão Refinar ficam atrás dela, e o clique não chega a nada.
  for (let i=0;i<3;i++){
    const temDiff = await p.evaluate(()=>/Compara[çc][ãa]o de Altera/i.test(document.body.innerText));
    if(!temDiff) break;
    const fechou = await p.evaluate(()=>{
      const a=[...document.querySelectorAll('button,span,div,a')]
        .filter(e=>['×','✕','x','X'].includes((e.textContent||'').trim()) && e.offsetParent);
      if(!a.length) return false; a[a.length-1].click(); return true;});
    if(!fechou) await p.keyboard.press('Escape');
    await sleep(2500);
    console.log('comparação fechada');
  }
  const cx = p.getByPlaceholder(/Digite sua mensagem/i).first();
  if (!(await cx.count())) { console.log('!! caixa de mensagem não encontrada'); await b.close(); return; }
  await cx.focus(); await p.keyboard.type(PEDIDO,{delay:2});
  await sleep(600); await shot(p,'spec-pedido-de-correcao');
  // "Refinar" (não "Analisar": Analisar só resume, não altera o documento)
  const bt = p.getByRole('button',{name:/refinar/i}).first();
  if (!(await bt.count())) { console.log('!! botão Refinar não encontrado'); await b.close(); return; }
  await bt.click({timeout:20000,force:true}).catch(async e=>{console.log('clique falhou:',String(e.message).split('\n')[0]);});
  console.log('▷ refino disparado às', new Date().toLocaleTimeString());
  await sleep(8000); await shot(p,'spec-refino-em-andamento');
  for (let i=0;i<60;i++){
    await sleep(15000);
    const t = await p.evaluate(()=>document.body.innerText);
    if (/Refinamento conclu|Especificação refinada|Vers[ãa]o 2/i.test(t)) { console.log('▷ concluído'); break; }
  }
  await sleep(3000); await shot(p,'spec-refino-concluido');
  await b.close();
})();
