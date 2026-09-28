const { chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs=require('fs');
const TELAS=JSON.parse(fs.readFileSync(process.env.CLAUDE_JOB_DIR+'/tmp/telas_app.json','utf8'));
const log=(...a)=>console.log(new Date().toISOString().slice(11,19),...a);
(async()=>{
  const b=await chromium.launch({args:['--no-sandbox','--disable-gpu']});
  const p=await b.newPage({viewport:{width:1600,height:1050}});
  p.on('pageerror',e=>log('ERRO:',String(e).slice(0,100)));
  await p.goto('http://localhost:3016/',{waitUntil:'domcontentloaded',timeout:60000});
  await p.waitForTimeout(6000);
  const ins=p.locator('input');
  if(await ins.count()>=2){
    await ins.nth(0).pressSequentially('helena@biobyte.hosp',{delay:8});
    await ins.nth(1).pressSequentially('sentinela2026',{delay:8});
    await p.locator('button:has-text("Entrar")').first().click().catch(()=>{});
    await p.waitForTimeout(4000);
  }
  const rel=[];
  for(const t of TELAS){
    try{
      const alvo=p.locator(`text="${t.label}"`).first();
      if(!await alvo.count()){ rel.push({...t,veredito:'FORA DO MENU'}); log(`FORA DO MENU | ${t.label.slice(0,48)}`); continue; }
      await alvo.click({timeout:6000});
      await p.waitForTimeout(2000);
      const m=await p.evaluate(()=>({
        linhas: document.querySelectorAll('table tbody tr').length,
        campos: document.querySelectorAll('input,select,textarea').length,
        graficos: document.querySelectorAll('canvas,.recharts-wrapper').length,
        botoes: Array.from(document.querySelectorAll('button')).map(x=>x.innerText.trim()).filter(Boolean),
        texto: (document.body.innerText||'')
      }));
      const agente=m.botoes.some(x=>/Executar com IA/i.test(x));
      const semAcao=/não vinculada a uma tarefa|Tarefa não definida/.test(m.texto);
      const vazio=/Sem registros para exibir|Sem dados para o período|Nenhum registro/.test(m.texto);
      const v = semAcao?'SEM ACAO' : (m.linhas>0?'COM DADOS' : (agente?'AGENTE PRONTO' : (vazio?'VAZIA':(m.campos>2?'FORMULARIO':'SIMPLES'))));
      rel.push({...t,veredito:v,linhas:m.linhas,campos:m.campos,graficos:m.graficos,agente});
      log(`${v.padEnd(13)} | ${t.label.slice(0,46).padEnd(48)} linhas=${m.linhas} campos=${m.campos}${agente?' [IA]':''}`);
    }catch(e){ rel.push({...t,veredito:'NAO ABRIU'}); log(`NAO ABRIU     | ${t.label.slice(0,46)}`); }
  }
  fs.writeFileSync(process.env.CLAUDE_JOB_DIR+'/tmp/validacao_telas.json', JSON.stringify(rel,null,2));
  const c={}; rel.forEach(r=>c[r.veredito]=(c[r.veredito]||0)+1);
  log('=== RESUMO ===', JSON.stringify(c));
  await b.close();
})().catch(e=>{console.log('FALHOU:',e.message);process.exit(1);});
