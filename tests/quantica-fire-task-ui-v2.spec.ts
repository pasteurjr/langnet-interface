/**
 * V2 — Fix dos seletores de aba (matching com emoji prefix) +
 * espera 60s pelo task_completed antes de fotografar Outputs/Logs.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const WS_URL = 'ws://localhost:5002';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica-live-v2');
let stepIdx = 1;
const ts = (label: string) => path.join(OUT, `${String(stepIdx++).padStart(2, '0')}-${label}.png`);

async function login(page: Page) {
  const res = await page.request.post(`${API_BASE}/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
    headers: { 'Content-Type': 'application/json' },
  });
  const body = await res.json();
  await page.goto(`${APP_BASE}/login`);
  await page.evaluate(([t, u]) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
    localStorage.setItem('user', JSON.stringify(u));
  }, [body.access_token, body.user]);
}

async function clickTab(page: Page, label: string) {
  await page.evaluate((needle: string) => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => (b.textContent || '').toLowerCase().includes(needle.toLowerCase())) as HTMLButtonElement | undefined;
    btn?.click();
  }, label);
  await page.waitForTimeout(800);
}

test.beforeAll(() => { fs.mkdirSync(OUT, { recursive: true }); });

test('Quântica live: aba a aba', async ({ page }) => {
  test.setTimeout(240_000);
  page.on('console', (m) => { if (m.type() === 'error') console.log('[error]', m.text().slice(0, 250)); });
  await login(page);

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net?autoconnect=${encodeURIComponent(WS_URL)}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(7000);

  // Conecta
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /^conectar$/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('conectado'), fullPage: true });

  // Seleciona suggest_weekly_themes no dropdown
  await page.evaluate(() => {
    const sel = document.querySelector('select') as HTMLSelectElement | null;
    if (sel) {
      sel.value = 'suggest_weekly_themes';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await page.waitForTimeout(300);

  // Preenche body JSON
  await page.evaluate(() => {
    const ta = document.querySelector('textarea') as HTMLTextAreaElement | null;
    if (ta) {
      const payload = JSON.stringify({
        mes: 6, ano: 2026,
        personas_ativas: ['CTO scale-up B2B brasileiras'],
        pilares_ativos: [{ nome: 'IA Generativa para Vendas', frequencia_dias: 7, tom_voz: 'didático' }],
      }, null, 2);
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
      setter?.call(ta, payload);
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: ts('form-preenchido'), fullPage: true });

  // Executa
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /executar/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('apos-executar'), fullPage: true });

  // Aguarda task_completed
  let completed = false;
  for (let i = 0; i < 60; i++) {
    await page.waitForTimeout(2000);
    const ok = await page.evaluate(() => {
      const m = (document.body.textContent || '').match(/completed:\s*(\d+)/);
      return m && parseInt(m[1]) > 0;
    });
    if (ok) { completed = true; break; }
  }
  console.log('TASK COMPLETED:', completed);
  await page.screenshot({ path: ts('completed-na-aba-execucao'), fullPage: true });

  // Outputs
  await clickTab(page, 'outputs');
  await page.screenshot({ path: ts('aba-outputs'), fullPage: true });

  // Inputs
  await clickTab(page, 'inputs');
  await page.screenshot({ path: ts('aba-inputs'), fullPage: true });

  // Logs
  await clickTab(page, 'logs');
  await page.screenshot({ path: ts('aba-logs'), fullPage: true });

  // Operação
  await clickTab(page, 'operação');
  await page.screenshot({ path: ts('aba-operacao'), fullPage: true });

  // Dump conteúdo da aba Outputs (texto)
  await clickTab(page, 'outputs');
  const outputsText = await page.evaluate(() => {
    const panel = document.querySelector('[style*="right: 0"]') as HTMLElement | null;
    return (panel?.textContent || '').slice(0, 2000);
  });
  console.log('=== Outputs textContent ===');
  console.log(outputsText);
});
