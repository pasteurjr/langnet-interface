// Abre a Especificação e fotografa trechos legíveis dela.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '156', 10);
const ALVOS = process.argv.slice(3);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const nome=t=>t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,42);
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/task-execution-flow`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  await shot(p,'sequencia-documento-aberto');
  // Fechar a "Comparação de Alterações", que abre sozinha após um refino e cobre a tela.
  for (let i=0;i<3;i++){
    const tem = await p.evaluate(()=>/Compara[çc][ãa]o de Altera/i.test(document.body.innerText));
    if(!tem) break;
    const ok = await p.evaluate(()=>{const a=[...document.querySelectorAll('button,span,div,a')]
      .filter(e=>['×','✕','x','X'].includes((e.textContent||'').trim())&&e.offsetParent);
      if(!a.length) return false; a[a.length-1].click(); return true;});
    if(!ok) await p.keyboard.press('Escape');
    await sleep(2500);
  }
  // abrir o texto: o cartão do documento traz Editar / Visualizar / Exportar PDF
  const vis = p.getByRole('button',{name:/visualizar/i}).first();
  if (await vis.count()) { await vis.click({force:true}).catch(()=>{}); await sleep(5000);
                           console.log('documento aberto para leitura'); }
  else console.log('!! botão Visualizar não encontrado');
  for (const alvo of ALVOS) {
    const achou = await p.evaluate((txt)=>{
      const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
      const a=norm(txt);
      // Buscar SÓ dentro do visualizador. A conversa da etapa contém o texto do pedido de
      // refino, que repete os nomes das seções — sem esta restrição a captura casa no chat.
      const modal=[...document.querySelectorAll('div')]
        .find(e=>/Visualizar Documento/i.test((e.textContent||'').slice(0,200)) && e.querySelectorAll('h1,h2,h3,h4').length>3);
      const raiz = modal || document;
      const tit=[...raiz.querySelectorAll('h1,h2,h3,h4,h5')];
      let c=tit.filter(e=>{const t=norm(e.textContent||'').replace(/^\d+(\.\d+)*[.)]?\s*/,'').trim();
                           return t.startsWith(a);});
      if(!c.length) c=tit.filter(e=>norm(e.textContent||'').includes(a));
      if(!c.length) c=[...raiz.querySelectorAll('p,li,td,strong')]
        .filter(e=>norm(e.textContent||'').includes(a)&&(e.textContent||'').length<400);
      if(!c.length) return null;
      c[0].scrollIntoView({block:'start'});
      return (c[0].textContent||'').trim().slice(0,70);
    }, alvo);
    if(!achou){ console.log('!! não achei:', alvo); continue; }
    console.log('→', achou); await sleep(1200);
    await shot(p,'seq-'+nome(alvo));
  }
  await b.close();
})();
