// Abre a versão vigente do documento de requisitos e fotografa TRECHOS LEGÍVEIS dele.
// Uso: node drive_trechos_doc.js <numero-inicial> "<titulo1>" "<titulo2>" ...
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '130', 10);
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
  await p.goto(`http://localhost:3001/project/${PROJ}/documents`,{waitUntil:'domcontentloaded'});
  await sleep(8000);
  // navegar ate a versao vigente: Historico -> lista de analises -> sessao -> versao mais recente
  await p.getByRole('button',{name:/hist[óo]rico/i}).first().click({force:true}).catch(()=>{});
  await sleep(3000);
  const voltar = p.getByRole('button',{name:/voltar para lista de documentos/i}).first();
  if (await voltar.count()) { await voltar.click({force:true}).catch(()=>{}); await sleep(2500); }
  // Escolher a sessão que TEM a versão 2 (a refinada). A lista vem da mais recente para a mais
  // antiga, e a mais recente pode ser outra análise — foi o que aconteceu na primeira tentativa.
  // Por padrão pega a análise MAIS RECENTE. Com SESSAO_COM_V2=1 no ambiente, procura a que
  // tem versão 2 (útil para mostrar o antes/depois de um refino).
  const querV2 = process.env.SESSAO_COM_V2 === '1';
  let achouV2 = false;
  for (let i = 0; i < (querV2 ? 4 : 1) && !achouV2; i++) {
    const clicou = await p.evaluate((idx)=>{
      const a=[...document.querySelectorAll('div,li,tr,button')]
        .filter(e=>/Document Analysis/i.test(e.textContent||'')&&(e.textContent||'').length<200
                   &&e.querySelectorAll('div,li,tr').length<4);
      if(a.length<=idx) return false; a[idx].click(); return true;
    }, i);
    if(!clicou) break;
    await sleep(4000);
    achouV2 = querV2 ? await p.evaluate(()=>/Vers[ãa]o 2/i.test(document.body.innerText)) : true;
    console.log(`sessão ${i+1}: ${achouV2 ? 'escolhida' : 'só versão 1, tentando a próxima'}`);
    if(!achouV2){
      const v=p.getByRole('button',{name:/voltar para lista de documentos/i}).first();
      if(await v.count()){ await v.click({force:true}).catch(()=>{}); await sleep(2500); }
    }
  }
  const ver = p.getByText(/Clique para visualizar/i).first();   // a primeira e a versao mais recente
  if (await ver.count()) { await ver.click({force:true}).catch(()=>{}); await sleep(4000); }
  const fechar = p.getByRole('button',{name:/^fechar$/i}).first();
  if (await fechar.count()) { await fechar.click({force:true}).catch(()=>{}); await sleep(2500); }
  // A "Comparação de Alterações" abre SOZINHA quando a conversa tem um refino, e cobre a tela.
  // Sem fechá-la, o clique em Visualizar não chega ao cartão do documento.
  for (let i=0;i<3;i++){
    const temDiff = await p.evaluate(()=>/Compara[çc][ãa]o de Altera/i.test(document.body.innerText));
    if(!temDiff) break;
    const fechou = await p.evaluate(()=>{
      const alvo=[...document.querySelectorAll('button,span,div,a')]
        .filter(e=>['×','✕','x','X'].includes((e.textContent||'').trim()) && e.offsetParent);
      if(!alvo.length) return false;
      alvo[alvo.length-1].click(); return true;
    });
    if(!fechou) await p.keyboard.press('Escape');
    await sleep(2500);
  }
  // abrir o texto do documento: o cartão traz Editar / Visualizar / Exportar PDF
  const visual = p.getByRole('button',{name:/visualizar/i}).first();
  if (await visual.count()) { await visual.click({force:true}).catch(()=>{}); await sleep(4000);
                              console.log('documento aberto para leitura'); }
  else console.log('!! botão Visualizar não encontrado');
  await shot(p,'documento-de-requisitos-vigente');
  for (const alvo of ALVOS) {
    const achou = await p.evaluate((txt)=>{
      const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
      const a=norm(txt);
      // Preferir TÍTULO que COMEÇA com o alvo. Sem isso o buscador cai na primeira menção
      // qualquer do termo — a palavra "Recomendações" aparece na descrição de um ator muito
      // antes da seção 16, e a captura sai do lugar errado.
      const titulos=[...document.querySelectorAll('h1,h2,h3,h4')];
      let cand=titulos.filter(e=>{const t=norm(e.textContent||'').replace(/^\d+[.)]?\s*/,'').trim();
                                  return t.startsWith(a) || t.replace(/^\d+\.\s*/,'').startsWith(a);});
      if(!cand.length) cand=titulos.filter(e=>norm(e.textContent||'').includes(a));
      if(!cand.length) cand=[...document.querySelectorAll('p,li,td,strong')]
        .filter(e=>norm(e.textContent||'').includes(a) && (e.textContent||'').length<400);
      if(!cand.length) return null;
      const el=cand[0];
      el.scrollIntoView({block:'start'});
      return (el.textContent||'').trim().slice(0,70);
    }, alvo);
    if(!achou){ console.log('!! não achei na tela:', alvo); continue; }
    console.log('→', achou);
    await sleep(1200);
    await shot(p,'trecho-'+nome(alvo));
  }
  await b.close();
})();
