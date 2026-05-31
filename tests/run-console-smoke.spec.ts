import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'run-console');
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

test('Run Console: clica Executar → console aparece → recebe linhas → para', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Carrega sessão existente
  const sessions = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .filter((el) => /completed/i.test(el.textContent || ''))
      .map((el) => (el.textContent || '').slice(0, 60));
  });
  console.log('Sessões disponíveis (completed):', sessions);
  expect(sessions.length, 'precisa de pelo menos uma sessão completed').toBeGreaterThan(0);

  // Clica na primeira sessão completed
  await page.evaluate(() => {
    const sess = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((el) => /completed/i.test(el.textContent || ''));
    (sess as HTMLElement)?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('session-loaded'), fullPage: true });

  // Clica em "▶ Executar"
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /^▶ Executar$/.test((b.textContent || '').trim())) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('console-opened'), fullPage: true });

  // Confere que console apareceu
  const hasConsole = await page.evaluate(() => {
    return (document.body.textContent || '').includes('Console de Execução');
  });
  expect(hasConsole, 'Console não apareceu').toBeTruthy();

  // Aguarda algumas linhas chegarem ([runner] mensagens iniciais aparecem em ~5s)
  const gotRunnerLines = await page.waitForFunction(
    () => /\[runner\]/.test(document.body.textContent || ''),
    null,
    { timeout: 60_000, polling: 1500 },
  ).then(() => true).catch(() => false);
  await page.screenshot({ path: ts('runner-output'), fullPage: true });
  expect(gotRunnerLines, 'Nenhuma linha [runner] aparecida em 60s').toBeTruthy();

  // Para a execução (vai matar o pip install)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /parar/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('after-stop'), fullPage: true });

  // Confere status final
  const finalStatus = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      hasStopped: txt.includes('STOPPED'),
      hasCrashed: txt.includes('CRASHED'),
      hasInstalling: txt.includes('INSTALLING'),
      hasRunning: txt.includes('RUNNING') && !txt.includes('INSTALLING'),
    };
  });
  console.log('Status final:', finalStatus);
  // Esperamos STOPPED ou CRASHED (porque foi parado durante pip install)
  expect(finalStatus.hasStopped || finalStatus.hasCrashed, 'deveria estar STOPPED ou CRASHED após parar').toBeTruthy();
});
