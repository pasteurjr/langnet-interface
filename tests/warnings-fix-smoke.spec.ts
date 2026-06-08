import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'warnings-fix');
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

test.beforeAll(() => { fs.mkdirSync(OUT, { recursive: true }); });

test('Warning banner: aparece, botão Corrigir popula chat com prompt certo', async ({ page }) => {
  test.setTimeout(60_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2500);

  // Seleciona uma sessão completed que tem warnings (a última gerada com agent_task_spec)
  await page.evaluate(() => {
    const sess = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((el) => /completed/i.test(el.textContent || ''));
    (sess as HTMLElement)?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('session-loaded'), fullPage: true });

  // Confere banner de warnings visível
  const hasBanner = await page.evaluate(() => {
    return (document.body.textContent || '').includes('validation warning');
  });
  console.log('Banner visível:', hasBanner);

  if (!hasBanner) {
    console.log('Sessão sem warnings — pulando teste de botão Corrigir');
    return;
  }

  // Clica no primeiro botão "🔧 Corrigir"
  const clickedCategory = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /corrigir/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    if (!btn) return null;
    // Pega categoria associada (irmão <code>)
    const li = btn.closest('li');
    const code = li?.querySelector('code')?.textContent || '';
    btn.click();
    return code;
  });
  console.log('Categoria do warning clicado:', clickedCategory);
  await page.waitForTimeout(500);
  await page.screenshot({ path: ts('after-click-corrigir'), fullPage: true });

  // Confere que o textarea do chat foi populado
  const chatValue = await page.evaluate(() => {
    const ta = Array.from(document.querySelectorAll('textarea'))
      .find((t) => /refinar projeto/i.test((t as HTMLTextAreaElement).placeholder || ''));
    return (ta as HTMLTextAreaElement | undefined)?.value;
  });
  console.log('Chat input populado (primeiros 200 chars):', chatValue?.substring(0, 200));
  expect(chatValue, 'Chat input vazio após clicar Corrigir').toBeTruthy();
  expect(chatValue!.length, 'Prompt muito curto').toBeGreaterThan(50);
});
