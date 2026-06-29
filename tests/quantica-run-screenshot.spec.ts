/**
 * Screenshot da Quântica em execução: tela de Code Generation com o botão Executar.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const CODE_GEN_SESSION = '10b2a8f3-dcc4-4daa-a42a-a92816a30ff5';
const RUN_ID = 'f8bc8fc4-0509-40c8-9d3d-8b0b1abe789d';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica-running');
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

test('Quântica: code gen com run ativo', async ({ page }) => {
  test.setTimeout(120_000);
  await login(page);

  // Code Generation page
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);

  // Clica na sessão
  await page.evaluate((sid) => {
    const items = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'));
    const target = items.find((el) => (el.getAttribute('title') || '').includes(sid));
    (target as HTMLElement | undefined)?.click();
  }, CODE_GEN_SESSION);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('code-gen-session'), fullPage: true });

  // Tenta navegar pra runs do session
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation?session=${CODE_GEN_SESSION}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2500);

  // Procura botão Executar
  const runButtonFound = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /executar|run/i.test(b.textContent || '')
    );
    return btn ? (btn.textContent || '').trim() : null;
  });
  console.log('Botão Executar visível:', runButtonFound);

  // Screenshot da tela com tudo
  await page.screenshot({ path: ts('final-with-run'), fullPage: true });
});
