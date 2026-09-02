const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs'); const BASE='http://localhost:3001', PROJ='bab9d113-eff1-474f-8acc-0abfa516cd7d';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots'; let N=202;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,tag)=>{const f=`${OUT}/${N}-langnet-${tag}.png`; await p.screenshot({path:f,timeout:60000}); console.log('📸',f.split('/').pop()); N++;};
(async()=>{
  const b=await firefox.launch({headless:true, executablePath:'/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox'});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  await p.goto(BASE,{waitUntil:'domcontentloaded'}); await p.evaluate(t=>{localStorage.setItem('accessToken',t);localStorage.setItem('token',t);},TOKEN);
  await p.goto(`${BASE}/project/${PROJ}/code-generation`,{waitUntil:'domcontentloaded'}); await sleep(4000);
  // garante a sessão v7 selecionada (primeira da lista)
  await p.getByText('code_gen_20260902_172156').first().click().catch(()=>{}); await sleep(1500);
  for (const f of ['ws-server/tasks.yaml','ws-server/mcp_tools.py','ws-server/adapters.py','ws-server/websocket_server.py']) {
    await p.getByText(f,{exact:true}).first().click({timeout:8000}).catch(e=>console.log('x',f)); await sleep(1500);
    await shot(p,'arquivo-'+f.split('/').pop().replace(/\W/g,'_'));
  }
  // rola o tasks.yaml até a classificação NHSN (execution_reason) e captura
  await p.getByText('ws-server/tasks.yaml',{exact:true}).first().click().catch(()=>{}); await sleep(1200);
  const txt=await p.locator('body').innerText().catch(()=> '');
  console.log('tasks.yaml mostra execution_reason?', /execution_reason/.test(txt), '| aliases visíveis?', /MCP_OUT_ALIASES/.test(txt));
  await b.close(); console.log('DONE');
})().catch(e=>{console.error('FALHOU',e.message);process.exit(1);});
