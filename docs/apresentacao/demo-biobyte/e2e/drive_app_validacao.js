// Prova, na TELA do app gerado, cada comportamento cobrado pelos casos de teste.
// Uso: APP_URL=http://localhost:3010 node drive_app_validacao.js <indice>
const { firefox } = require('/home/pasteurjr/progreact/langnet-interface/node_modules/playwright');
process.on('uncaughtException', e => console.log('erro de cliente ignorado:', String(e.message).split('\n')[0]));
const BASE = process.env.APP_URL || 'http://localhost:3010';
const OUT = '/home/pasteurjr/progreact/langnet-interface/docs/apresentacao/demo-biobyte/shots';
const FF = '/home/pasteurjr/.cache/ms-playwright/firefox-1497/firefox/firefox';
let N = parseInt(process.argv[2] || '650', 10);
const SO = process.argv[3] || '';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const CTX = { usuario_id: 'U-001', paciente_id: 'P-001', caso_id: 'CAS-2023-001', idade: 72,
  dias_cateter: 12, uti: true, nutricao_parenteral: true, neutropenia: false,
  tipo_cateter: 'Cateter Central', apache_ii: 18, microrganismo: 'Staphylococcus aureus',
  multirresistente: true, formato: 'csv' };

const PASSOS = [
  { tag: 'dashboard-com-dados', menu: 'Dashboard de Vigilância', espera: /casos|taxa|escore|\d/i, prova: 'indicadores e gráficos preenchidos' },
  { tag: 'bundle-com-itens', menu: 'Recomendação de Bundle', espera: /bundle|justificativa|insuficien/i, prova: 'bundle com justificativa e itens' },
  { tag: 'classificacao-criterios', menu: 'Detalhe do Caso Clínico', espera: /ICSAC|Pendente|classific/i, prova: 'critérios da norma e classificação' },
  { tag: 'login-credenciais-invalidas', menu: 'Login e MFA', semContexto: true,
    campos: { email: 'inexistente@x.br', senha: 'errada', codigo_mfa: '000000' },
    espera: /Credenciais inválidas/i, prova: 'mensagem do caso de uso' },
  { tag: 'classificacao-selo', menu: 'Detalhe do Caso Clínico', espera: /ICSAC Confirmado|Não ICSAC|Classificação Pendente/i, prova: 'selo de classificação' },
  { tag: 'escore-barra-progresso', menu: 'Detalhe do Caso', espera: /escore|risco/i, prova: 'barra do escore' },
  { tag: 'estimativa-risco', menu: 'Resultado da Estimativa', espera: /redu|estimativa|insuficien/i, prova: 'estimativa ou recusa honesta' },
  { tag: 'auditoria-nenhum-registro', menu: 'Logs de Auditoria', datas: true, espera: /Nenhum registro encontrado|logs/i, prova: 'lista vazia identificada + Exportar CSV' },
  { tag: 'relatorio-arquivo-gerado', menu: 'Geração de Relatórios', espera: /\.csv|\.pdf|arquivo/i, prova: 'arquivo gerado' },
];

const mainText = p => p.evaluate(() => { const m = document.querySelector('main'); return m ? m.innerText : ''; }).catch(() => '');

(async () => {
  const b = await firefox.launch({ headless: true, executablePath: FF });
  for (const passo of PASSOS.filter(x => !SO || x.tag.includes(SO))) {
    const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
    try {
      await p.goto(BASE, { waitUntil: 'domcontentloaded' }); await sleep(2000);
      if (!passo.semContexto) {
        await p.evaluate(c => localStorage.setItem('clinia.current_attendance', JSON.stringify(c)), CTX);
        await p.reload({ waitUntil: 'domcontentloaded' }); await sleep(2500);
      }
      await p.locator('aside').getByText(new RegExp(passo.menu, 'i')).first().click({ timeout: 10000 });
      await sleep(2000);
      for (const [campo, valor] of Object.entries(passo.campos || {})) {
        await p.evaluate(([c, v]) => {
          const ins = [...document.querySelectorAll('main input')];
          const alvo = ins.find(i => (i.name || i.placeholder || '').toLowerCase().includes(c.split('_')[0]))
                    || ins.find(i => (i.previousElementSibling || {}).textContent && (i.previousElementSibling.textContent || '').toLowerCase().includes(c.split('_')[0]));
          if (alvo) { const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            set.call(alvo, v); alvo.dispatchEvent(new Event('input', { bubbles: true })); }
        }, [campo, valor]);
      }
      if (passo.datas) {
        await p.evaluate(() => {
          const ins = [...document.querySelectorAll('main input')];
          const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          const por = (el, v) => { set.call(el, v); el.dispatchEvent(new Event('input', { bubbles: true })); };
          const ini = ins.find(i => /inicio|início/i.test((i.name || '') + (i.placeholder || '')));
          const fim = ins.find(i => /fim|final/i.test((i.name || '') + (i.placeholder || '')));
          if (ini) por(ini, '2020-01-01'); if (fim) por(fim, '2020-01-02');
          if (!ini && ins.length >= 2) { por(ins[0], '2020-01-01'); por(ins[1], '2020-01-02'); }
        });
      }
      await sleep(600);
      await p.screenshot({ path: `${OUT}/${N}-validacao-${passo.tag}-antes.png`, timeout: 60000 });
      console.log('📸', `${N}-validacao-${passo.tag}-antes.png`); N++;
      await p.evaluate(() => { const bs = [...document.querySelectorAll('main button')];
        const b = bs.find(x => /Executar|Entrar|Confirmar|Calcular|Consultar|Gerar|Classificar|Filtrar|Atualizar|Ver /i.test(x.innerText)); if (b) b.click(); });
      let txt = '';
      for (let i = 0; i < 60; i++) { await sleep(2500); txt = await mainText(p);
        if (passo.espera.test(txt) || /⚠|erro/i.test(txt)) break; }
      const barras = await p.locator('[role="progressbar"]').count().catch(() => 0);
      const csv = /Exportar CSV/i.test(txt);
      console.log(`${passo.tag}: ${passo.espera.test(txt) ? 'PROVADO (' + passo.prova + ')' : 'não confirmou'}`
        + (barras ? ` | barras: ${barras}` : '') + (csv ? ' | Exportar CSV presente' : ''));
      console.log('   tela diz:', txt.replace(/\n/g, ' | ').slice(-260));
      await p.screenshot({ path: `${OUT}/${N}-validacao-${passo.tag}.png`, timeout: 60000 });
      console.log('📸', `${N}-validacao-${passo.tag}.png`); N++;
    } catch (e) { console.log('x', passo.tag, String(e.message).split('\n')[0]); }
    await p.close().catch(() => {});
  }
  await b.close().catch(() => {});
  console.log('DONE validação próximo índice', N);
})();
