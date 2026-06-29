/**
 * Captura tudo do projeto Quântica Comercial para o manual completo:
 *  - Telas de cada etapa do pipeline (Documents, Requirements, Specification, ATS,
 *    agents.yaml/tasks.yaml, TEF, Petri Net, Code Generation)
 *  - Conexão WS + execução de 3 tasks demo via ExecutionPanel
 *
 *  Tudo salvo em /home/pasteurjr/comercial-quantica/screenshots/ e demo/
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const REQ_EXECUTION_ID = '3a4ab218-b5b7-4f5c-b5ff-fc233ff29a00';
const CODE_GEN_SESSION = '7684959e-087c-4d06-85d6-673a3a2401ab';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const WS_URL = 'ws://localhost:5002';

const ROOT = '/home/pasteurjr/comercial-quantica';
const SHOTS = path.join(ROOT, 'screenshots');
const DEMO = path.join(ROOT, 'demo');

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

async function fireTask(page: Page, taskName: string, payload: any) {
  await page.evaluate((tn: string) => {
    const sel = document.querySelector('select') as HTMLSelectElement | null;
    if (sel) {
      sel.value = tn;
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }, taskName);
  await page.waitForTimeout(400);
  await page.evaluate((p: any) => {
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
}

async function waitCompletion(page: Page, before = 0, timeoutMs = 90_000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    await page.waitForTimeout(2000);
    const c = await page.evaluate(() => {
      const m = (document.body.textContent || '').match(/completed:\s*(\d+)/);
      return m ? parseInt(m[1], 10) : 0;
    });
    if (c > before) return c;
  }
  return -1;
}

test.beforeAll(() => {
  fs.mkdirSync(SHOTS, { recursive: true });
  fs.mkdirSync(DEMO, { recursive: true });
});

test('Manual Quântica: pipeline screens + 3 demo tasks', async ({ page }) => {
  test.setTimeout(600_000);
  page.on('console', (m) => {
    if (m.type() === 'error') console.log('[browser-err]', m.text().slice(0, 200));
  });
  await login(page);

  let step = 1;
  const shot = (label: string) =>
    path.join(SHOTS, `${String(step++).padStart(2, '0')}-${label}.png`);

  // ====== TELAS DO PIPELINE ======
  await page.goto(`${APP_BASE}/projects`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2500);
  await page.screenshot({ path: shot('projetos'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/documents`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: shot('documents'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/requirements/${REQ_EXECUTION_ID}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: shot('requirements'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/specification`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4500);
  await page.screenshot({ path: shot('specification'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/agent-task`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4500);
  await page.screenshot({ path: shot('agent-task-spec'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/generate-yaml`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4500);
  await page.screenshot({ path: shot('agents-tasks-yaml'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/task-execution-flow`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4500);
  await page.screenshot({ path: shot('task-execution-flow'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(8000);
  await page.screenshot({ path: shot('petri-net'), fullPage: true });

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);
  await page.evaluate((sid) => {
    const items = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'));
    const target = items.find((el) => (el.getAttribute('title') || '').includes(sid));
    (target as HTMLElement | undefined)?.click();
  }, CODE_GEN_SESSION);
  await page.waitForTimeout(2800);
  await page.screenshot({ path: shot('code-generation'), fullPage: true });

  // ====== EXECUÇÃO AO VIVO ======
  let demoStep = 1;
  const dshot = (label: string) =>
    path.join(DEMO, `${String(demoStep++).padStart(2, '0')}-${label}.png`);

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
  await page.screenshot({ path: dshot('conectado'), fullPage: true });

  // Demo 1: suggest_weekly_themes
  await fireTask(page, 'suggest_weekly_themes', {
    mes: 6,
    ano: 2026,
    personas_ativas: ['CTO de scale-up B2B brasileira'],
    pilares_ativos: [
      { nome: 'IA Generativa para Vendas', frequencia_dias: 7, tom_voz: 'didático' },
    ],
  });
  await page.screenshot({ path: dshot('task-1-disparada'), fullPage: true });
  const c1 = await waitCompletion(page, 0);
  console.log('Demo 1 (suggest_weekly_themes) completou:', c1);
  await page.screenshot({ path: dshot('task-1-completed'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: dshot('task-1-outputs'), fullPage: true });
  const out1 = await page.evaluate(() => (document.body.textContent || '').slice(0, 6000));
  fs.writeFileSync(path.join(DEMO, '01-suggest_weekly_themes-output.txt'), out1);

  await clickTab(page, 'execução');

  // Demo 2: identify_target_companies
  await fireTask(page, 'identify_target_companies', {
    icp: {
      setor: 'SaaS B2B',
      porte: '50-500 funcionários',
      regiao: 'Brasil',
      tecnologias_alvo: ['Salesforce', 'HubSpot', 'AWS'],
    },
    limite: 5,
  });
  await page.screenshot({ path: dshot('task-2-disparada'), fullPage: true });
  const c2 = await waitCompletion(page, c1 > 0 ? c1 : 1);
  console.log('Demo 2 (identify_target_companies) completou:', c2);
  await page.screenshot({ path: dshot('task-2-completed'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: dshot('task-2-outputs'), fullPage: true });
  const out2 = await page.evaluate(() => (document.body.textContent || '').slice(0, 6000));
  fs.writeFileSync(path.join(DEMO, '02-identify_target_companies-output.txt'), out2);

  await clickTab(page, 'execução');

  // Demo 3: generate_blog_article
  await fireTask(page, 'generate_blog_article', {
    tema: 'Como CrewAI + Petri Nets revolucionam automação de marketing B2B',
    persona: {
      cargo: 'CMO',
      setor: 'SaaS B2B',
      dores: ['ROI de marketing', 'qualificação de leads', 'volume de conteúdo'],
    },
    pilar: 'Inovação em Vendas',
    tom_voz: 'autoridade técnica com exemplos práticos',
    palavras: 1200,
  });
  await page.screenshot({ path: dshot('task-3-disparada'), fullPage: true });
  const c3 = await waitCompletion(page, c2 > 0 ? c2 : 2, 120_000);
  console.log('Demo 3 (generate_blog_article) completou:', c3);
  await page.screenshot({ path: dshot('task-3-completed'), fullPage: true });
  await clickTab(page, 'outputs');
  await page.screenshot({ path: dshot('task-3-outputs'), fullPage: true });
  const out3 = await page.evaluate(() => (document.body.textContent || '').slice(0, 8000));
  fs.writeFileSync(path.join(DEMO, '03-generate_blog_article-output.txt'), out3);

  // Logs final
  await clickTab(page, 'logs');
  await page.screenshot({ path: dshot('logs-completos'), fullPage: true });
  await clickTab(page, 'operação');
  await page.screenshot({ path: dshot('operacao-resumo'), fullPage: true });
});
