/**
 * Re-roda apenas tasks 2 e 3 com timeouts mais longos.
 * Mantém task1-* já capturados.
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
const DEMO = '/home/pasteurjr/comercial-quantica/demo';

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

async function clickTab(page: Page, needle: string) {
  await page.evaluate((n: string) => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find((b) => (b.textContent || '').toLowerCase().includes(n.toLowerCase())) as
      | HTMLButtonElement
      | undefined;
    btn?.click();
  }, needle);
  await page.waitForTimeout(900);
}

async function fireTask(page: Page, taskName: string, payload: any) {
  await page.evaluate((tn: string) => {
    const sel = document.querySelector('select') as HTMLSelectElement | null;
    if (sel) {
      sel.value = tn;
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }, taskName);
  await page.waitForTimeout(400);
  await page.evaluate((p: any) => {
    const ta = document.querySelector('textarea') as HTMLTextAreaElement | null;
    if (ta) {
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
      setter?.call(ta, JSON.stringify(p, null, 2));
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }, payload);
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /executar/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
}

async function waitTerminal(page: Page, before: { completed: number; errors: number }, timeoutMs: number) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    await page.waitForTimeout(2000);
    const counts = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const c = (txt.match(/completed:\s*(\d+)/) || [, '0'])[1];
      const e = (txt.match(/errors:\s*(\d+)/) || [, '0'])[1];
      return { completed: parseInt(c, 10), errors: parseInt(e, 10) };
    });
    if (counts.completed > before.completed) return { ...counts, kind: 'completed' as const };
    if (counts.errors > before.errors) return { ...counts, kind: 'error' as const };
  }
  return { completed: -1, errors: -1, kind: 'timeout' as const };
}

test('demo 2 e 3 com timeout grande', async ({ page }) => {
  test.setTimeout(900_000);
  page.on('console', (m) => { if (m.type() === 'error') console.log('[err]', m.text().slice(0, 200)); });
  await login(page);

  let step = 20;
  const shot = (label: string) =>
    path.join(DEMO, `${String(step++).padStart(2, '0')}-${label}.png`);

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net?autoconnect=${encodeURIComponent(WS_URL)}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(7000);
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /^conectar$/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2500);

  // === Task 2 (3min timeout) ===
  await fireTask(page, 'identify_target_companies', {
    icp: { setor: 'SaaS B2B', porte: '50-500 funcionários', regiao: 'Brasil', tecnologias_alvo: ['Salesforce', 'HubSpot'] },
    limite: 3,
  });
  await page.screenshot({ path: shot('task2-disparada'), fullPage: true });
  const r2 = await waitTerminal(page, { completed: 0, errors: 0 }, 200_000);
  console.log('TASK 2 result:', r2);
  await page.screenshot({ path: shot('task2-execucao'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: shot('task2-outputs'), fullPage: true });
  fs.writeFileSync(path.join(DEMO, 'task2-output.txt'),
    await page.evaluate(() => (document.body.textContent || '').slice(0, 8000)));
  await clickTab(page, 'execução');

  // === Task 3 (4min timeout) ===
  await fireTask(page, 'generate_blog_article', {
    tema: 'CrewAI e Petri Nets em automação de marketing B2B',
    persona: { cargo: 'CMO', setor: 'SaaS B2B' },
    pilar: 'Inovação',
    tom_voz: 'autoridade técnica',
    palavras: 500,
  });
  await page.screenshot({ path: shot('task3-disparada'), fullPage: true });
  const r3 = await waitTerminal(page, r2.kind === 'completed' ? { completed: r2.completed, errors: r2.errors } : { completed: 0, errors: r2.errors }, 240_000);
  console.log('TASK 3 result:', r3);
  await page.screenshot({ path: shot('task3-execucao'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: shot('task3-outputs'), fullPage: true });
  fs.writeFileSync(path.join(DEMO, 'task3-output.txt'),
    await page.evaluate(() => (document.body.textContent || '').slice(0, 12000)));

  await clickTab(page, 'logs');
  await page.screenshot({ path: shot('logs-final'), fullPage: true });
  await clickTab(page, 'operação');
  await page.screenshot({ path: shot('operacao-final'), fullPage: true });
});
