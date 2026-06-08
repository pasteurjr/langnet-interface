/**
 * Smoke: clicar "Baixar ZIP" em sessão com warnings → confirm aparece →
 * cancelar não baixa; aceitar baixa o ZIP. Confirma headers de validation.
 */
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'download-warn');
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

test('Download warn: confirm aparece com categorias; cancelar bloqueia; aceitar baixa ZIP', async ({ page }) => {
  test.setTimeout(60_000);

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Carrega primeira sessão completed
  await page.evaluate(() => {
    const sess = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((el) => /completed/i.test(el.textContent || ''));
    (sess as HTMLElement)?.click();
  });
  await page.waitForTimeout(2500);

  // 1) Primeiro clique: cancelar no dialog → não deve baixar
  let dialogMsg1 = '';
  let cancelled = false;
  page.once('dialog', async (d) => {
    dialogMsg1 = d.message();
    console.log('Dialog 1 msg:', d.message().substring(0, 200));
    cancelled = true;
    await d.dismiss();  // cancelar
  });

  // Sem listener de download — qualquer download seria erro
  let downloadHappened = false;
  page.once('download', () => { downloadHappened = true; });

  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /baixar zip/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('after-cancel'), fullPage: true });

  expect(cancelled, 'Dialog não apareceu').toBeTruthy();
  expect(dialogMsg1.includes('warning'), `Dialog não menciona warnings: ${dialogMsg1.substring(0, 100)}`).toBeTruthy();
  expect(dialogMsg1.includes('tools_orphan'), 'Dialog não lista categoria tools_orphan').toBeTruthy();
  expect(downloadHappened, 'Download disparou apesar do usuário cancelar').toBeFalsy();
  console.log('✅ Cancel funciona');

  // 2) Segundo clique: aceitar → deve baixar
  page.once('dialog', async (d) => {
    console.log('Dialog 2 - aceitando');
    await d.accept();
  });
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 15_000 }),
    page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button'))
        .find((b) => /baixar zip/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
      btn?.click();
    }),
  ]);
  const dest = path.join(OUT, 'downloaded.zip');
  await download.saveAs(dest);
  const size = fs.statSync(dest).size;
  console.log('ZIP baixado:', size, 'bytes');
  expect(size, 'ZIP vazio').toBeGreaterThan(1000);
  await page.screenshot({ path: ts('after-accept'), fullPage: true });
});
