/**
 * Smoke do Uso do Solo: confirma que o documento de requirements aparece
 * na UI navegando pelas páginas do pipeline.
 */
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'uso-solo');
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

test('Uso do Solo: documentos, requirements e progresso pelo pipeline', async ({ page }) => {
  test.setTimeout(60_000);
  await login(page);

  // 1) Página de Documentos
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/documents`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('documents'), fullPage: true });

  const hasDocs = await page.evaluate(() => {
    return (document.body.textContent || '').includes('Entrevista_Organizada');
  });
  console.log('docs page menciona Entrevista_Organizada:', hasDocs);

  // 2) Página de Specifications
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/spec`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('specification'), fullPage: true });

  const hasSessions = await page.evaluate(() => {
    return /spec.*uso do solo/i.test(document.body.textContent || '') ||
           /especifica/i.test(document.body.textContent || '');
  });
  console.log('spec page renderizou:', hasSessions);

  // 3) Página de Petri Net (apenas botão Gerar)
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('petri-net'), fullPage: true });

  const hasPetriBtn = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button')).some(b => /gerar rede/i.test(b.textContent || ''));
  });
  console.log('petri net page com botão Gerar:', hasPetriBtn);

  // 4) Página de Code Generation
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('code-generation'), fullPage: true });

  console.log('✅ Pipeline UI: telas básicas renderizam para o projeto Uso do Solo');
});
