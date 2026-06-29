import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica');
let stepIdx = 100;
const ts = (label: string) => path.join(OUT, `${String(stepIdx++).padStart(3, '0')}-${label}.png`);

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

test('Telas do projeto Quântica', async ({ page }) => {
  test.setTimeout(30_000);
  await login(page);

  await page.goto(`${APP_BASE}/projects`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('projetos-lista'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/documents`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3500);
  await page.screenshot({ path: ts('doc-uploaded'), fullPage: true });
});
