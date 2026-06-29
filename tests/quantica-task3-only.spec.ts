/**
 * Roda apenas a task 3 (generate_blog_article) com timeout enorme e prompt curto.
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

test('task 3 sozinha com 8min timeout', async ({ page }) => {
  test.setTimeout(900_000);
  await login(page);

  let step = 30;
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

  // Task 3 com prompt minimal
  await page.evaluate(() => {
    const sel = document.querySelector('select') as HTMLSelectElement | null;
    if (sel) {
      sel.value = 'generate_blog_article';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });
  await page.waitForTimeout(400);
  const payload = {
    tema: 'CrewAI para automação de vendas',
    persona: 'CMO de SaaS B2B',
    palavras: 300,
  };
  await page.evaluate((p) => {
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
  await page.screenshot({ path: shot('task3-disparada-v2'), fullPage: true });

  // Aguarda até 7 minutos
  const t0 = Date.now();
  let lastSeen = '';
  while (Date.now() - t0 < 420_000) {
    await page.waitForTimeout(3000);
    const txt = await page.evaluate(() => {
      const m = (document.body.textContent || '').match(/(task_start|completed|errors)[^L]*Limpar/);
      return m ? m[0].slice(0, 100) : '';
    });
    if (txt !== lastSeen) { console.log('[mark]', txt); lastSeen = txt; }
    const done = await page.evaluate(() => {
      const m1 = (document.body.textContent || '').match(/completed:\s*(\d+)/);
      const m2 = (document.body.textContent || '').match(/errors:\s*(\d+)/);
      return { c: m1 ? parseInt(m1[1], 10) : 0, e: m2 ? parseInt(m2[1], 10) : 0 };
    });
    if (done.c > 0 || done.e > 0) {
      console.log('TERMINAL:', done);
      break;
    }
  }

  await page.screenshot({ path: shot('task3-execucao-v2'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: shot('task3-outputs-v2'), fullPage: true });
  fs.writeFileSync(path.join(DEMO, 'task3-output.txt'),
    await page.evaluate(() => (document.body.textContent || '').slice(0, 12000)));
});
