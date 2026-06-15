/**
 * Captura visual final do pipeline completo do Uso do Solo:
 * Petri Net renderizada + Code Generation com warnings + ZIP download.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const CODE_GEN_SESSION = 'c3b90965-78fa-451f-9bdf-d1d718158d4b';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'uso-solo-final');
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

test('Pipeline Uso do Solo completo: Petri Net + Code Gen visualmente', async ({ page }) => {
  test.setTimeout(60_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);

  // 1) Página Petri Net — deve renderizar 12 lugares + 12 trans + 15 arcos + 8 agentes
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(6000);
  await page.screenshot({ path: ts('petri-net'), fullPage: true });

  const petriStats = await page.evaluate(() => ({
    circles: document.querySelectorAll('svg circle').length,
    rects: document.querySelectorAll('svg rect').length,
  }));
  console.log('Petri Net canvas:', petriStats);

  // 2) Code Generation — carrega a sessão recém-criada
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);

  // Clica na sessão alvo
  await page.evaluate((sid) => {
    const items = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'));
    const target = items.find((el) => (el.getAttribute('title') || '').includes(sid));
    (target as HTMLElement | undefined)?.click();
  }, CODE_GEN_SESSION);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('code-gen-session'), fullPage: true });

  // Confere warnings + arquivos
  const cgInfo = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    const categories = Array.from(document.querySelectorAll('li code')).map(c => (c.textContent || '').trim());
    const files = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .map(d => (d.textContent || '').trim())
      .filter(t => /\.(py|yaml|json|md|txt|yml)$|^Dockerfile$/.test(t));
    return { warningCategories: categories, fileNames: files.slice(0, 15) };
  });
  console.log('Warnings:', cgInfo.warningCategories);
  console.log('Arquivos visíveis:', cgInfo.fileNames);
});
