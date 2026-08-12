// Smoke-test E2E do fluxo clínico da ClinIA pela UI (Fase 0). Um paciente percorre
// triagem -> pré-diagnóstico -> encaminhamento -> prontuário -> consulta. Grava os IDs
// acumulados (atendimento corrente) em APP_DIR/e2e-carry.json para verify_chain.py conferir.
// Config via env: FRONTEND_PORT, APP_DIR, NODE_PLAYWRIGHT.
const PW = process.env.NODE_PLAYWRIGHT || '/home/pasteurjr/progreact/langnet-interface/node_modules/playwright';
const { chromium } = require(PW);
const fs = require('fs');
const PORT = process.env.FRONTEND_PORT || '3007';
const APP = process.env.APP_DIR || '/home/pasteurjr/clinia-app5';
const BASE = `http://localhost:${PORT}`;
const stamp = String(Date.now()).slice(-6);
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);
const getCarry = (pg) => pg.evaluate(() => { try { return JSON.parse(localStorage.getItem('clinia.current_attendance') || '{}'); } catch (e) { return {}; } });
async function nav(pg, m) { await pg.getByText(m, { exact: false }).first().click({ timeout: 8000 }).catch(() => {}); await pg.waitForTimeout(2000); }
async function fillByLabel(pg, sub, val) { return pg.evaluate(({ sub, val }) => { const L = [...document.querySelectorAll('label')]; const lab = L.find(l => (l.innerText || '').toLowerCase().includes(sub.toLowerCase())); if (!lab) return false; const el = lab.parentElement && (lab.parentElement.querySelector('input') || lab.parentElement.querySelector('textarea')); if (!el) return false; const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', { bubbles: true })); return true; }, { sub, val }); }
async function selByLabel(pg, sub) { return pg.evaluate((sub) => { const L = [...document.querySelectorAll('label')]; const lab = L.find(l => (l.innerText || '').toLowerCase().includes(sub.toLowerCase())); if (!lab) return false; const sel = lab.parentElement && lab.parentElement.querySelector('select'); if (!sel || sel.options.length < 2) return false; const s = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set; s.call(sel, sel.options[1].value); sel.dispatchEvent(new Event('change', { bubbles: true })); return sel.options[1].text; }, sub); }
async function exec(pg) { await pg.getByText('Executar com IA', { exact: false }).first().click({ timeout: 8000 }).catch(() => {}); }
async function waitRes(pg, re, maxs) { for (let i = 0; i < maxs / 3; i++) { await pg.waitForTimeout(3000); const t = await pg.evaluate(() => document.body.innerText); if (re.test(t)) return true; if (/⚠/.test(t) && i > 3) return false; } return false; }

(async () => {
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const pg = await (await b.newContext({ viewport: { width: 1500, height: 1050 } })).newPage();
  await pg.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await pg.waitForTimeout(2500);
  log('[1] triagem'); await nav(pg, 'Recepção & Triagem');
  const vals = [`Smoke ${stamp}`, '33' + stamp + '0', '1966-02-11', '11900000000', 'Amil', 'Dor toracica opressiva irradia braco esq, sudorese', '160/100', '120', '37.0', '92'];
  const ins = await pg.$$('input'); for (let i = 0; i < Math.min(ins.length, vals.length); i++) await ins[i].fill(vals[i]);
  await exec(pg); const ok1 = await waitRes(pg, /ATENDIMENTO_ID/i, 300); const c1 = await getCarry(pg); log('[1] ok=' + ok1, JSON.stringify(c1));
  log('[2] pré-diagnóstico'); await nav(pg, 'Geração de Pré-diagnóstico');
  let ok2 = false, c2 = {}; for (let a = 0; a < 2 && !ok2; a++) { await exec(pg); ok2 = await waitRes(pg, /hipotes|nivel_confianca|pre_diagnostico_id/i, 300); c2 = await getCarry(pg); if (c2.pre_diagnostico_id) { ok2 = true; break; } }
  log('[2] ok=' + ok2, JSON.stringify(c2));
  log('[3] seleção de médico'); await nav(pg, 'Seleção de Médico'); await pg.waitForTimeout(3000);
  await selByLabel(pg, 'especialidade'); await selByLabel(pg, 'medico'); await selByLabel(pg, 'médico'); await pg.waitForTimeout(500);
  await exec(pg); const ok3 = await waitRes(pg, /encaminhamento_id|sucesso/i, 60); const c3 = await getCarry(pg); log('[3] ok=' + ok3, JSON.stringify(c3));
  log('[4] prontuário'); await nav(pg, 'Registro/Prontuário'); await pg.waitForTimeout(2500);
  await fillByLabel(pg, 'queixa', 'Dor toracica opressiva'); await fillByLabel(pg, 'resumo', 'Quadro sugestivo de SCA.'); await pg.waitForTimeout(500);
  await exec(pg); const ok4 = await waitRes(pg, /prontuario_id|sucesso|status/i, 90); const c4 = await getCarry(pg); log('[4] ok=' + ok4, JSON.stringify(c4));
  log('[5] consulta'); await nav(pg, 'Consulta Médica'); await pg.waitForTimeout(2000);
  await fillByLabel(pg, 'diagnóstico final', 'SCA confirmada'); await fillByLabel(pg, 'conduta', 'UTI coronariana'); await fillByLabel(pg, 'prescri', 'AAS 300mg');
  await exec(pg); const ok5 = await waitRes(pg, /diagnostico|conduta|resultado|sucesso|persistido/i, 300); log('[5] ok=' + ok5);
  const cf = await getCarry(pg);
  const summary = { c1, c2, c3, c4, cf, ok: { ok1, ok2, ok3, ok4, ok5 } };
  fs.writeFileSync(APP + '/e2e-carry.json', JSON.stringify(summary, null, 2));
  log('FIM', JSON.stringify(cf));
  await b.close();
  const allok = ok1 && ok3 && ok4;  // etapas determinísticas críticas (agênticas podem variar no LLM)
  process.exit(allok ? 0 : 1);
})().catch(e => { console.error('FATAL', e.message); process.exit(2); });
