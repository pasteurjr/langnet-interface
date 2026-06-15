import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'uso-solo-yamls');
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

test('Tela de YAMLs do Uso do Solo', async ({ page }) => {
  test.setTimeout(30_000);
  await login(page);

  // Tenta página de yaml-generation que listaria as sessões
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/yaml-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);
  await page.screenshot({ path: ts('yaml-page'), fullPage: true });

  const info = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      hasAgentsYaml: /document_converter_agent/i.test(txt),
      hasTasksYaml: /convert_uploaded_legislation/i.test(txt),
      hasSessionsList: txt.includes('yaml') || txt.includes('YAML'),
    };
  });
  console.log('yaml page:', info);
});
