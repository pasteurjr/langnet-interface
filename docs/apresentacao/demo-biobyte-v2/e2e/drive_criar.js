const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
const fs = require('fs');
process.on('uncaughtException', e => console.log('cliente:', String(e.message).split('\n')[0]));
let N = parseInt(process.argv[2] || '3', 10);
const BASE='http://localhost:3001';
const TOKEN=fs.readFileSync('/tmp/langnet_token.txt','utf8').trim();
const OUT='/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte-v2/shots';
const FF='/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const shot=async(p,t)=>{const f=`${OUT}/${String(N).padStart(3,'0')}-${t}.png`;await p.screenshot({path:f,timeout:60000});console.log('📸',f.split('/').pop());N++;};
(async()=>{
  const b=await firefox.launch({headless:true,executablePath:FF});
  const p=await b.newPage({viewport:{width:1500,height:950}});
  p.on('console',m=>{if(m.type()==='error')console.log('ERRO:',m.text().slice(0,110));});
  await p.goto(BASE,{waitUntil:'domcontentloaded'});
  // A interface guarda o USUARIO alem do token: sem o objeto 'user' no armazenamento local, o
  // formulario de criar projeto para em "Usuario nao autenticado" antes de chamar o servidor.
  await p.evaluate(t=>{
    localStorage.setItem('accessToken',t); localStorage.setItem('token',t);
    localStorage.setItem('user', JSON.stringify({
      id:'11111111-1111-1111-1111-111111111111', name:'Admin Tropical', email:'admin@tropical.com'}));
  },TOKEN);
  await p.goto(`${BASE}/projects`,{waitUntil:'domcontentloaded'}); await sleep(6000);
  await p.evaluate(()=>{const b=[...document.querySelectorAll('button,a')].find(e=>/novo projeto|criar projeto/i.test(e.textContent||'')); if(b)b.click();});
  await sleep(3000);
  const r = await p.evaluate(() => {
    const setar=(el,v)=>{const s=Object.getOwnPropertyDescriptor(el.tagName==='TEXTAREA'?window.HTMLTextAreaElement.prototype:window.HTMLInputElement.prototype,'value').set;
      s.call(el,v); el.dispatchEvent(new Event('input',{bubbles:true}));};
    const feitos=[];
    for (const c of document.querySelectorAll('input,textarea,select')) {
      const rot=((c.closest('div')?.textContent)||'').toLowerCase();
      if (c.tagName==='SELECT') {
        let alvo=null;
        if (rot.includes('domínio')||rot.includes('dominio')) alvo=[...c.options].find(o=>/sa[úu]de|health/i.test(o.textContent));
        if (rot.includes('framework')) alvo=[...c.options].find(o=>/crewai/i.test(o.textContent));
        if (rot.includes('protocolo')) alvo=[...c.options].find(o=>/okf/i.test(o.textContent));
        if (rot.includes('llm')) alvo=[...c.options].find(o=>/local/i.test(o.textContent));
        if (rot.includes('memória')||rot.includes('memoria')) alvo=[...c.options].find(o=>/langchain/i.test(o.textContent));
        if (alvo){c.value=alvo.value;c.dispatchEvent(new Event('change',{bubbles:true}));feitos.push(rot.slice(0,14)+'='+alvo.textContent.trim().slice(0,18));}
      } else if (rot.includes('nome do projeto')) { setar(c,'BioByte Sentinela v3'); feitos.push('nome'); }
      else if (rot.includes('descrição')||rot.includes('descricao')) {
        setar(c,'Vigilância de Infecção de Corrente Sanguínea Associada a Cateter (ICSAC) para a Comissão de Controle de Infecção Hospitalar: prioriza pacientes por risco, confirma o caso pela microbiologia, recomenda o pacote de prevenção e estima a redução de risco — com registro auditável de cada decisão.');
        feitos.push('descrição');
      }
    }
    return feitos;
  });
  console.log('preenchido:', r.join(' | '));
  await sleep(800); await shot(p,'projeto-preenchido');
  // O clique por dentro da página não dispara o envio (o React não registra). Clique de verdade,
  // como o navegador faria — mesmo atrito já visto nas outras etapas.
  const alvo = p.getByRole('button', { name: /^Criar Projeto$/ }).last();
  await alvo.scrollIntoViewIfNeeded().catch(()=>{});
  await alvo.click({ timeout: 20000, force: true }).catch(async (e) => {
    console.log('clique normal falhou:', String(e.message).split('\n')[0]);
    await p.keyboard.press('Enter');
  });
  console.log('envio disparado'); await sleep(8000);
  const aviso = await p.evaluate(()=>{const t=document.body.innerText; const m=t.match(/(obrigat[óo]rio|inv[áa]lid|erro|falh)[^\n]{0,80}/i); return m?m[0]:'';});
  if (aviso) console.log('aviso na tela:', aviso);
  await shot(p,'projeto-criado');
  console.log('URL:', p.url());
  await b.close();
})();
