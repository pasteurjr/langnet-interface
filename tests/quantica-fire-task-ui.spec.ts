/**
 * Conecta + dispara task via UI do ExecutionPanel e captura cada etapa.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const WS_URL = 'ws://localhost:5002';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica-fire');
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

test('Quântica: conectar WS via UI, executar task, captura tudo', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'log') console.log(`[${m.type()}]`, m.text().slice(0,250)); });
  await login(page);

  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net?autoconnect=${encodeURIComponent(WS_URL)}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(7000);
  await page.screenshot({ path: ts('inicial'), fullPage: true });

  // Clica em "Conectar" (botão real)
  const conectouVia = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /conectar/i.test(b.textContent || '')
    ) as HTMLButtonElement | undefined;
    btn?.click();
    return btn ? btn.textContent : null;
  });
  console.log('Clicou:', conectouVia);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('apos-conectar'), fullPage: true });

  // Status
  const status1 = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      conectado: /CONECTADO/.test(txt),
      conectando: /CONECTANDO/.test(txt),
      erro: /Erro de conexão/.test(txt),
      tasksAvail: (txt.match(/(\d+)\s*tasks?\s*disponíveis/i) || [])[0] || '',
    };
  });
  console.log('Status pós-conectar:', status1);

  // Preenche task_name + input_data
  await page.evaluate(() => {
    const taskInput = Array.from(document.querySelectorAll('input')).find(i =>
      i.placeholder === 'task_name' || i.placeholder?.includes('task')
    ) as HTMLInputElement | undefined;
    if (taskInput) {
      taskInput.value = 'suggest_weekly_themes';
      taskInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    const ta = Array.from(document.querySelectorAll('textarea')).find(t =>
      t.placeholder?.includes('{') || (t.value || '').trim() === '{}'
    ) as HTMLTextAreaElement | undefined;
    if (ta) {
      const payload = JSON.stringify({
        mes: 6, ano: 2026,
        personas_ativas: ['CTO scale-up B2B'],
        pilares_ativos: [{ nome: 'IA Generativa', frequencia_dias: 7, tom_voz: 'didático' }],
      }, null, 2);
      ta.value = payload;
      ta.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: ts('form-preenchido'), fullPage: true });

  // Clica Executar
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /executar/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('apos-executar'), fullPage: true });

  // Aguarda completion (40s timeout)
  let completed = false;
  for (let i = 0; i < 30; i++) {
    await page.waitForTimeout(2000);
    const ok = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const completedMatch = txt.match(/completed:\s*(\d+)/);
      return completedMatch && parseInt(completedMatch[1]) > 0;
    });
    if (ok) { completed = true; break; }
  }
  console.log('task completed:', completed);

  await page.screenshot({ path: ts('execution-completed'), fullPage: true });

  // Clica em Outputs pra ver resultado
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /^outputs?$/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('aba-outputs-com-resultado'), fullPage: true });

  // Logs
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      /^logs?$/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: ts('aba-logs-completos'), fullPage: true });
});
