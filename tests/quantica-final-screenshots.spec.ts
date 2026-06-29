/**
 * Screenshots finais da Quântica Comercial — após pipeline completo.
 * Captura: dashboard, docs, requirements, spec, ATS, YAMLs, TEF, Petri Net, Code Gen.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const CODE_GEN_SESSION = '10b2a8f3-dcc4-4daa-a42a-a92816a30ff5';
const REQUIREMENTS_EXECUTION_ID = '3a4ab218-b5b7-4f5c-b5ff-fc233ff29a00';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica-final');
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

test('Quântica: capturas finais de cada etapa', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });
  await login(page);

  // 1) Projects dashboard
  await page.goto(`${APP_BASE}/projects`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('projects-dashboard'), fullPage: true });

  // 2) Documents
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/documents`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('documents'), fullPage: true });

  // 3) Requirements
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/requirements/${REQUIREMENTS_EXECUTION_ID}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: ts('requirements'), fullPage: true });

  // 4) Specifications
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/specification`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: ts('specification'), fullPage: true });

  // 5) Agent Task Spec (rota é /agent-task)
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/agent-task`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: ts('agent-task-spec'), fullPage: true });

  // 6) YAML Generation (agents + tasks juntos)
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/generate-yaml`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: ts('yaml-generation'), fullPage: true });

  // 8) Task Execution Flow
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/task-execution-flow`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: ts('task-execution-flow'), fullPage: true });

  // 9) Petri Net (deve renderizar 26 lugares + 25 trans + 58 arcos + 8 agentes)
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(8000);
  await page.screenshot({ path: ts('petri-net'), fullPage: true });

  const petriStats = await page.evaluate(() => ({
    circles: document.querySelectorAll('svg circle').length,
    rects: document.querySelectorAll('svg rect').length,
  }));
  console.log('Petri Net canvas:', petriStats);

  // 10) Code Generation — escolher a sessão alvo
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);
  await page.screenshot({ path: ts('code-gen-list'), fullPage: true });

  await page.evaluate((sid) => {
    const items = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'));
    const target = items.find((el) => (el.getAttribute('title') || '').includes(sid));
    (target as HTMLElement | undefined)?.click();
  }, CODE_GEN_SESSION);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('code-gen-session'), fullPage: true });

  const cgInfo = await page.evaluate(() => {
    const categories = Array.from(document.querySelectorAll('li code')).map(c => (c.textContent || '').trim());
    const files = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .map(d => (d.textContent || '').trim())
      .filter(t => /\.(py|yaml|json|md|txt|yml)$|^Dockerfile$|docker-compose/.test(t));
    return { warningCategories: categories, fileNames: files.slice(0, 20) };
  });
  console.log('Warnings:', cgInfo.warningCategories);
  console.log('Arquivos:', cgInfo.fileNames);
});
