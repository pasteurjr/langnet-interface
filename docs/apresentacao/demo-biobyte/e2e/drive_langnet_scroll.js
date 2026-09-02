const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs'); const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots'; let N=206;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`; await p.screenshot({path:f,timeout:60000}); console.log('📸',f.split('/').pop()); N++;};
async function openAndFind(p,file,needle,tag){
  await p.getByText(file,{exact:true}).first().click({timeout:8000}); await sleep(1500);
  let found=false;
  for(let i=0;i<60;i++){
    const loc=p.getByText(needle,{exact:false}).first();
    if(await loc.count().catch(()=>0)){ await loc.scrollIntoViewIfNeeded().catch(()=>{}); found=true; break; }
    // rola o painel de código (o elemento scrollável que contém o cabeçalho do arquivo)
    await p.mouse.move(1150,600); await p.mouse.wheel(0,1400); await sleep(250);
  }
  console.log(file,'→',needle, found?'ENCONTRADO':'não visível'); await sleep(600); await shot(p,tag);
}
(async()=>{
  const b=await firefox.launch({headless:true, executablePath:'/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox'});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  await p.goto(BASE,{waitUntil:'domcontentloaded'}); await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'domcontentloaded'}); await sleep(4000);
  await p.getByText('code_gen_20260902_172156').first().click().catch(()=>{}); await sleep(1500);
  await openAndFind(p,'ws-server/mcp_tools.py','MCP_OUT_ALIASES','mcp_tools-aliases');
  await openAndFind(p,'ws-server/tasks.yaml','execution_reason','tasks_yaml-portao-nhsn');
  await openAndFind(p,'ws-server/adapters.py',"input_data.get('classificacao_nhsn', input_data.get('is_icsac'))",'adapters-alinhamento');
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU',e.message);process.exit(1);});
