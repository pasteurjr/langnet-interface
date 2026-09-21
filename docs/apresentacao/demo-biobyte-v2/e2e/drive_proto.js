// Monta o protótipo, captura dentro da etapa e TAMBÉM aberto sozinho, fora do LangNet.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '230', 10);
const PROJ = fs.readFileSync('/tmp/proj_v2.txt','utf8').trim();
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:1000}});
  await p.goto('http://localhost:3001',{waitUntil:'domcontentloaded'});
  await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);
    localStorage.setItem('user',JSON.stringify({id:'11111111-1111-1111-1111-111111111111',name:'Admin Tropical',email:'admin@tropical.com'}));},TOKEN);
  await p.goto(`http://localhost:3001/project/${PROJ}/ui-spec`,{waitUntil:'domcontentloaded'});
  await sleep(9000);
  const bt = p.getByRole('button',{name:/prot[óo]tipo/i}).first();
  if (!(await bt.count())) { console.log('!! botão Protótipo não achado'); await b.close(); return; }
  await bt.click({force:true}).catch(()=>{});
  console.log('▷ montagem do protótipo às', new Date().toLocaleTimeString());
  for (let i=0;i<60;i++){ await sleep(5000);
    const t=await p.evaluate(()=>document.body.innerText);
    if (!/Montando|Gerando/i.test(t)) break; }
  await sleep(4000);
  await shot(p,'prototipo-dentro-da-etapa');
  // endereço do protótipo, para abrir FORA do LangNet
  const url = await p.evaluate(()=>{const f=document.querySelector('iframe[title="protótipo"]'); return f?f.getAttribute('src'):'';});
  console.log('endereço do protótipo:', url||'(não achado)');
  if (url) {
    const q=await b.newPage({viewport:{width:1500,height:1000}});
    await q.goto(url,{waitUntil:'domcontentloaded'}); await sleep(6000);
    await shot(q,'prototipo-fora-do-langnet');
    // O menu do protótipo fica na barra lateral e os itens NÃO são links: são elementos
    // clicáveis quaisquer. Procurar só por 'nav a' achava apenas os botões do formulário.
    const itens=await q.evaluate(()=>[...document.querySelectorAll('div,a,button,li')]
      .filter(e=>e.onclick && e.offsetParent && (e.textContent||'').trim().length<70)
      .map(e=>(e.textContent||'').replace(/^[•✦\s]+/,'').trim()).slice(0,40));
    console.log('telas do protótipo:', itens.join(' · ').slice(0,400));
    // percorre algumas telas do protótipo
    for (const alvo of (process.argv.slice(3))) {
      // Os itens do menu são <div> COM onclick e COM filhos (o marcador • é um elemento à
      // parte). Filtrar por "sem filhos" descartava todos — foi o que fez a navegação falhar
      // duas vezes. O que os identifica é ter onclick e texto curto.
      const ok=await q.evaluate((a)=>{const e=[...document.querySelectorAll('div,a,button,li')]
        .filter(x=>x.onclick && x.offsetParent && (x.textContent||'').trim().length<70)
        .find(x=>new RegExp(a,'i').test(x.textContent||''));
        if(!e) return false; e.click(); return true;},alvo);
      if(!ok){ console.log('!! tela não achada:',alvo); continue; }
      await sleep(2500); console.log('→',alvo);
      await shot(q,'proto-'+alvo.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').slice(0,32));
    }
  }
  await b.close();
})();
