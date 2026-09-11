// Regenera a ESPECIFICAÇÃO pela interface e captura cada passo para o roteiro do vídeo.
// O ponto do vídeo: as tarefas de pesquisa voltaram a usar a ferramenta de busca — a
// especificação anterior saiu com ZERO fontes.
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '1310', 10);
const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
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
  await p.goto(`${BASE}/project/${PROJ}/spec`,{waitUntil:'domcontentloaded'});
  await sleep(5000);
  console.log('tela:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,500));
  await shot(p,'spec-antes');
  // Origem: a etapa exige escolher o documento de REQUISITOS de onde a especificação nasce —
  // é a rastreabilidade do pipeline, e o botão fica desabilitado sem isso.
  const req = p.getByRole('button',{name:/Requisitos/i}).first();
  if (await req.count()) { await req.click({timeout:15000}); await sleep(3000); await shot(p,'spec-origem-modal'); }
  // O modal tem dois cliques: o CARTÃO do documento e depois a VERSÃO dele — é a
  // rastreabilidade da etapa (a especificação nasce de uma versão específica dos requisitos).
  const cartao = p.locator('text=/Document Analysis|Análise de Documento/i').first();
  if (await cartao.count()) { await cartao.click({timeout:15000}); await sleep(2500); }
  const verVersoes = p.locator('text=/ver vers/i').first();
  if (await verVersoes.count()) { await verVersoes.click({timeout:10000}).catch(()=>{}); await sleep(2500); }
  await shot(p,'spec-origem-versoes');
  // Terceiro clique: a VERSÃO escolhida ("Clique para visualizar"). São três passos de propósito —
  // a etapa amarra a especificação a uma versão específica dos requisitos.
  const verVersao = p.locator('text=/Clique para visualizar/i').first();
  if (await verVersao.count()) { await verVersao.click({timeout:15000}); await sleep(3000); }
  const conf = p.getByRole('button',{name:/Selecionar|Confirmar|Usar esta|OK/i}).first();
  if (await conf.count()) { await conf.click({timeout:10000}).catch(()=>{}); await sleep(2500); }
  await shot(p,'spec-origem-escolhida');
  const btn = p.getByRole('button',{name:/Gerar Especificação/i}).first();
  if (!await btn.count()) { console.log('!! botão Gerar Especificação não encontrado'); await b.close(); return; }
  const t0 = Date.now();
  await btn.click({timeout:20000});
  console.log('▷ geração disparada às', new Date().toLocaleTimeString());
  await sleep(4000); await shot(p,'spec-gerando');
  // a geração passa por 9 tarefas encadeadas; acompanha até terminar
  let ultimo='';
  for (let i=0;i<120;i++){
    await sleep(15000);
    const t = await p.evaluate(()=>document.body.innerText);
    const marca = (t.match(/(Gerando|Analisando|Compondo|Verificando|Validando|Formatando)[^\n|]{0,60}/)||[''])[0];
    if (marca && marca!==ultimo) { ultimo=marca; console.log(`  [${Math.round((Date.now()-t0)/1000)}s] ${marca}`); }
    if (!/Gerando\.\.\./.test(t) && /UC-0|Casos de Uso|Especificação Funcional/i.test(t)) break;
  }
  console.log(`▷ terminou em ${Math.round((Date.now()-t0)/1000)}s`);
  await sleep(3000);
  await shot(p,'spec-pronta');
  console.log('final:', (await p.evaluate(()=>document.body.innerText)).replace(/\n/g,' | ').slice(0,400));
  await b.close();
})();
