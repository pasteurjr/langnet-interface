// Dirige a interface do app gerado (BioByte) e captura telas p/ o vídeo.
// uso: node drive_app.js <tour|forms|petri> [startIndex]
const { firefox: chromium } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
const MODE = process.argv[2] || 'tour'; let N = parseInt(process.argv[3] || '86', 10);
const BASE = 'http://localhost:3002';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const RES = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/e2e/app_drive_results.json';
const results = fs.existsSync(RES) ? JSON.parse(fs.readFileSync(RES,'utf8')) : {};
const sleep = ms => new Promise(r => setTimeout(r, ms));
const SCREENS = [
 ["login-mfa","Login e MFA"],["importacao-microbiologia","Importação de Microbiologia"],
 ["previa-resultados-microbiologia","Prévia de Resultados de Microbiologia"],
 ["detalhe-caso-clinico-classificacao","Detalhe do Caso Clínico (Visão de Classificação)"],
 ["alerta-mdr","Alerta MDR"],["detalhe-caso","Detalhe do Caso"],["recomendacao-bundle","Recomendação de Bundle"],
 ["resultado-estimativa-risco","Resultado da Estimativa de Risco"],["dashboard-vigilancia","Dashboard de Vigilância"],
 ["gestao-de-usuarios","Gestão de Usuários"],["logs-auditoria","Logs de Auditoria"],["geracao-relatorios","Geração de Relatórios"],
 ["alertas","Alertas"],["casos","Casos"],["escores_risco","Escores Risco"],["logs_auditoria","Logs Auditoria"],
 ["microbiologias","Microbiologias"],["pacientes","Pacientes"],["tratamentos","Tratamentos"],["usuarios","Usuarios"]];
const FILL = [ // [regex no rótulo/nome normalizado, valor]
 [/amostra/,"HMC-88213"],[/caso/,"CAS-2023-001"],[/paciente/,"P-001"],[/mail/,"ana@hospital.br"],[/senha/,"x"],
 [/mfa|codigo|código|token/,"123456"],[/idade/,"72"],[/cateter|dias/,"12"],[/usuario|usuário|admin/,"U-001"],
 [/nome/,"Dr. Carlos Silva"],[/papel|perfil|cargo/,"Enfermeiro"],[/hash/,"x9f2a"],[/microrganismo|organismo/,"Staphylococcus aureus"],
 [/apache/,"18"],[/data|inicio|início/,"2026-08-01"],[/fim/,"2026-09-02"],[/tipo/,"Cateter Central"],[/acao|ação/,"CREATE_USER"],
 [/pergunta|mensagem|consulta|texto|descri/,"Qual é a classificação NHSN do caso CAS-2023-001 e por quê?"]];
const norm = s => (s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
const shot = async (p, tag) => { const f = `${OUT}/${String(N).padStart(2,'0')}-app-${tag}.png`; await p.screenshot({path:f, fullPage:false}); console.log('📸', f.split('/').pop()); N++; return f; };
async function goScreen(p, label){ const esc = label.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const it = p.locator('aside').getByText(new RegExp('^[^A-Za-z0-9]*'+esc+'\\s*$')).first(); await it.scrollIntoViewIfNeeded().catch(()=>{}); await it.click({timeout:8000}); await sleep(900); }
async function fillForm(p){
  const filled = [];
  const n = await p.locator('main input:not([type=file]):not([type=checkbox]), main textarea, main select').count();
  for (let i=0;i<n;i++){
    const el = p.locator('main input:not([type=file]):not([type=checkbox]), main textarea, main select').nth(i);
    const tag = await el.evaluate(e=>e.tagName.toLowerCase()).catch(()=>'');
    const label = await el.evaluate(e=>{ let x=e; for(let k=0;k<4&&x;k++){ const l=x.previousElementSibling; if(l&&/label|div|span/i.test(l.tagName)&&l.textContent.trim()) return l.textContent.trim(); x=x.parentElement; } return e.getAttribute('placeholder')||e.getAttribute('name')||''; }).catch(()=>'');
    const key = norm(label);
    if (tag==='select'){ const v = await el.evaluate(s=>{const o=[...s.options].find(o=>o.value); return o?o.value:'';}).catch(()=>''); if(v){ await el.selectOption(v).catch(()=>{}); filled.push([label,v]); } continue; }
    const hit = FILL.find(([re])=>re.test(key)); const val = hit ? hit[1] : 'teste';
    await el.fill(String(val)).catch(()=>{}); filled.push([label,val]);
  }
  const cb = p.locator('main input[type=checkbox]'); const c = await cb.count(); for(let i=0;i<c;i++){ await cb.nth(i).check().catch(()=>{}); }
  return filled;
}
async function submitAndWait(p, maxMs=150000){
  const before = await p.locator('main').innerText().catch(()=>'' );
  const btn = p.locator('main button:not([disabled])').filter({hasNotText:/projetos|Reset|passo/}).last();
  const txt = await btn.innerText().catch(()=> '');
  await btn.click({timeout:8000}).catch(e=>console.log('  (sem botão clicável)', e.message.split('\n')[0]));
  const t0 = Date.now(); let after = before;
  while (Date.now()-t0 < maxMs){ await sleep(2500); after = await p.locator('main').innerText().catch(()=> ''); const busy = await p.locator('main button[disabled]').count().catch(()=>0);
    if (after !== before && busy===0 && !/Executando|Processando|Aguarde|\.\.\.$/.test(after.slice(-40))) break; }
  const delta = after.replace(before,'').trim().slice(0,600);
  return { button: txt, secs: Math.round((Date.now()-t0)/1000), result: delta };
}
(async()=>{
  const b = await chromium.launch({headless:true, executablePath:'/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox'}); const p = await b.newPage({viewport:{width:1500,height:950}});
  p.on('dialog', d=>d.dismiss().catch(()=>{}));
  await p.goto(BASE, {waitUntil:'domcontentloaded'}); await p.locator('aside').waitFor({timeout:60000}); await sleep(1500);
  if (MODE==='tour'){
    await shot(p,'home');
    for (const [id,label] of SCREENS){ try{ await goScreen(p,label); await shot(p,`tela-${id}`);}catch(e){ console.log('x',label,e.message.split('\n')[0]); } }
  }
  if (MODE==='forms'){
    const targets = SCREENS.slice(0,12); // as 12 telas de negócio (as 8 restantes são cadastros)
    for (const [id,label] of targets){
      try{ await goScreen(p,label); const filled = await fillForm(p); await shot(p,`form-${id}-preenchido`);
        const r = await submitAndWait(p); await shot(p,`form-${id}-resposta`);
        results[id] = {label, filled, ...r}; console.log(`  ${id}: [${r.button}] ${r.secs}s → ${r.result.slice(0,140).replace(/\n/g,' ')}`);
      }catch(e){ console.log('x',label,e.message.split('\n')[0]); results[id]={label, error:e.message.split('\n')[0]}; }
      fs.writeFileSync(RES, JSON.stringify(results,null,1));
    }
  }
  if (MODE==='petri'){
    await p.locator('aside').getByText('Admin / Petri').first().click(); await sleep(2500); await shot(p,'petri-executor');
    await p.getByRole('button',{name:/Execução/}).first().click().catch(()=>{}); await sleep(800);
    await p.getByRole('button',{name:/Executar tudo/}).first().click({timeout:8000}); console.log('▷ Executar tudo disparado');
    const t0=Date.now(); let k=0; const marks=[15000,45000,90000,150000,240000,330000];
    while (Date.now()-t0 < 360000){ await sleep(3000); const el=Date.now()-t0; if(k<marks.length && el>=marks[k]){ await shot(p,`petri-exec-${Math.round(el/1000)}s`); k++; }
      const runningDisabled = await p.getByRole('button',{name:/Executar tudo/}).first().isDisabled().catch(()=>true); if(!runningDisabled && el>20000) break; }
    await shot(p,'petri-exec-final');
    for (const tab of ['Logs','Outputs','Inputs','Operação']){ await p.getByRole('button',{name:new RegExp(tab)}).first().click().catch(()=>{}); await sleep(1200); await shot(p,`petri-aba-${norm(tab)}`); }
    const logs = await p.locator('main').innerText().catch(()=> ''); results['petri']={secs:Math.round((Date.now()-t0)/1000), logs_tail: logs.slice(-1500)}; fs.writeFileSync(RES, JSON.stringify(results,null,1));
  }
  await b.close(); console.log('DONE', MODE, 'próximo índice', N);
})().catch(e=>{ console.error('FALHOU', e.message); process.exit(1); });
