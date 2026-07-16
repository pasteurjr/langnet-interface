/**
 * V2: captura Code Generation com sessão + adapters.py e tasks.yaml abertos.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/tmp/uso-solo-pipeline/validation-screens';

const PROJECTS = [
  { label: 'quantica', projectId: 'b55ef718-0073-44d4-b279-11df89403e92' },
  { label: 'uso-solo', projectId: 'a1391183-f348-4a78-8773-8046b90a7676' },
];

test('Code Gen deep screenshots (session + files)', async ({ page }) => {
  test.setTimeout(600_000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(2000);

  for (const proj of PROJECTS) {
    await page.goto(`${APP}/project/${proj.projectId}/code-generation`);
    await page.waitForTimeout(5000);

    // Clica na sessão mais recente (primeiro item da lista)
    const firstSession = page.locator('text=/^code_gen_/').first();
    if (await firstSession.count() > 0) {
      await firstSession.click().catch(() => {});
      await page.waitForTimeout(3000);
      await page.screenshot({ path: `${OUT}/${proj.label}-cg-session-selected.png`, fullPage: true });

      // Tenta abrir adapters.py
      const adaptersLink = page.locator('text=/adapters\\.py/').first();
      if (await adaptersLink.count() > 0) {
        await adaptersLink.click().catch(() => {});
        await page.waitForTimeout(2000);
        await page.screenshot({ path: `${OUT}/${proj.label}-cg-adapters.png`, fullPage: true });

        // Rola pra parte com _deterministic
        const editor = page.locator('.monaco-editor, textarea, pre').first();
        if (await editor.count() > 0) {
          await editor.evaluate((el) => el.scrollTop = el.scrollHeight);
          await page.waitForTimeout(1500);
          await page.screenshot({ path: `${OUT}/${proj.label}-cg-adapters-bottom.png`, fullPage: true });
        }
      }

      // tasks.yaml
      const tasksLink = page.locator('text=/tasks\\.yaml/').first();
      if (await tasksLink.count() > 0) {
        await tasksLink.click().catch(() => {});
        await page.waitForTimeout(2000);
        await page.screenshot({ path: `${OUT}/${proj.label}-cg-tasks-yaml.png`, fullPage: true });
      }
    }
  }
});
