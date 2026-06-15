/**
 * Smoke fase 1: valida que o banner mostra warnings das novas categorias
 * missing_runtime_dep e missing_runtime_env após PUT (revalidate).
 * Confirma que cada warning ganha botão "🔧 Corrigir" funcional.
 */
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const TARGET_SESSION = 'e54656b9-f23e-4384-99fb-33eee5f8f2bb'; // sessão com PyPDF2
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'missing-dep');
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

test('Validator categoriza missing_runtime_dep e missing_runtime_env corretamente', async ({ page }) => {
  test.setTimeout(60_000);

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Clica na sessão alvo (procura por id no tooltip)
  await page.evaluate((sid) => {
    const items = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'));
    const target = items.find((el) => (el.getAttribute('title') || '').includes(sid));
    (target as HTMLElement | undefined)?.click();
  }, TARGET_SESSION);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('session-loaded'), fullPage: true });

  // Confere que banner mostra as novas categorias
  const bannerInfo = await page.evaluate(() => {
    const categories = Array.from(document.querySelectorAll('li code')).map(c => (c.textContent || '').trim());
    const buttons = Array.from(document.querySelectorAll('button')).map(b => (b.textContent || '').trim());
    return {
      categories,
      countFixButtons: buttons.filter(t => t === '🔧 Corrigir').length,
      countAutoFixButtons: buttons.filter(t => t === '🚀 Corrigir e enviar').length,
    };
  });
  console.log('categorias no banner:', bannerInfo.categories);
  console.log('botões Corrigir:', bannerInfo.countFixButtons);
  console.log('botões Auto-fix:', bannerInfo.countAutoFixButtons);

  expect(bannerInfo.categories.includes('missing_runtime_dep'),
    `categoria missing_runtime_dep ausente. visto: ${bannerInfo.categories.join(', ')}`).toBeTruthy();
  expect(bannerInfo.categories.includes('missing_runtime_env'),
    `categoria missing_runtime_env ausente. visto: ${bannerInfo.categories.join(', ')}`).toBeTruthy();
  expect(bannerInfo.countFixButtons, '🔧 Corrigir deve ter um por categoria').toBeGreaterThanOrEqual(2);

  // Clica no 🔧 Corrigir de missing_runtime_dep — deve popular chat com prompt específico
  const clicked = await page.evaluate(() => {
    const lis = Array.from(document.querySelectorAll('li'));
    const targetLi = lis.find(li => {
      const code = li.querySelector('code')?.textContent?.trim();
      return code === 'missing_runtime_dep';
    });
    const btn = targetLi?.querySelector('button') as HTMLButtonElement | undefined;
    btn?.click();
    return !!btn;
  });
  console.log('clicked Corrigir missing_runtime_dep:', clicked);
  await page.waitForTimeout(800);

  const chatValue = await page.evaluate(() => {
    const ta = Array.from(document.querySelectorAll('textarea'))
      .find((t) => /refinar projeto/i.test((t as HTMLTextAreaElement).placeholder || ''));
    return (ta as HTMLTextAreaElement | undefined)?.value || '';
  });
  console.log('chat populado (preview):', chatValue.substring(0, 200));
  await page.screenshot({ path: ts('chat-populated'), fullPage: true });

  expect(chatValue.includes('requirements.txt'),
    `prompt deveria mencionar requirements.txt. Got: ${chatValue.substring(0, 100)}`).toBeTruthy();
  expect(chatValue.includes('PyPDF2') || chatValue.includes('docx') || chatValue.includes('numpy'),
    `prompt deveria listar imports faltantes. Got: ${chatValue.substring(0, 200)}`).toBeTruthy();

  console.log(`✅ missing_runtime_dep + missing_runtime_env funcionam end-to-end na UI`);
});
