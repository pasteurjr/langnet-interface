/**
 * Validação E2E — captura visual do estado atual dos 2 projetos após:
 *  1. tasks.yaml chunked v4 (placeholder {var} correto)
 *  2. agent snake_case
 *  3. Opção B (adapters.py com <task>_deterministic)
 *
 * Não faz asserts de conteúdo — o objetivo é documentar o que o usuário
 * vai encontrar em cada tela dos dois projetos.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/tmp/uso-solo-pipeline/validation-screens';

const PROJECTS = [
  {
    label: 'quantica',
    projectId: 'b55ef718-0073-44d4-b279-11df89403e92',
    displayName: 'Quântica Comercial',
  },
  {
    label: 'uso-solo',
    projectId: 'a1391183-f348-4a78-8773-8046b90a7676',
    displayName: 'Uso do Solo',
  },
];

const TABS = [
  { key: 'requirements',     path: '/requirements',      wait: 4000 },
  { key: 'spec',             path: '/spec',              wait: 4000 },
  { key: 'data-model',       path: '/data-model',        wait: 4000 },
  { key: 'agent-task',       path: '/agent-task',        wait: 4000 },
  { key: 'yaml-generation',  path: '/yaml-generation',   wait: 4000 },
  { key: 'petri-net',        path: '/petri-net',         wait: 6000 },
  { key: 'code-generation',  path: '/code-generation',   wait: 5000 },
];

test('Validação visual E2E dos 2 projetos', async ({ page }) => {
  test.setTimeout(600_000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  fs.mkdirSync(OUT, { recursive: true });

  // ---- Login ----
  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${OUT}/00-logged-in.png`, fullPage: true });

  // ---- Lista de projetos ----
  await page.goto(`${APP}/projects`);
  await page.waitForTimeout(3500);
  await page.screenshot({ path: `${OUT}/01-projects-list.png`, fullPage: true });

  // ---- Para cada projeto: percorre as abas ----
  for (const proj of PROJECTS) {
    const prefix = `${proj.label}`;

    for (const tab of TABS) {
      const url = `${APP}/project/${proj.projectId}${tab.path}`;
      await page.goto(url).catch(() => {});
      await page.waitForTimeout(tab.wait);
      await page.screenshot({
        path: `${OUT}/${prefix}-${tab.key}.png`,
        fullPage: true,
      });
    }

    // ---- Code Generation: tenta abrir as sub-abas se existirem ----
    await page.goto(`${APP}/project/${proj.projectId}/code-generation`);
    await page.waitForTimeout(4000);
    const codeTabs = ['adapters.py', 'tasks.yaml', 'agents.yaml', 'petri_net.json', 'websocket_server.py'];
    for (const ct of codeTabs) {
      const link = page.locator(`text="${ct}"`).first();
      if (await link.count() > 0) {
        await link.click().catch(() => {});
        await page.waitForTimeout(1200);
        await page.screenshot({
          path: `${OUT}/${prefix}-code-${ct.replace(/[^\w]/g, '_')}.png`,
          fullPage: true,
        });
      }
    }
  }
});
