/**
 * Etapa 4c — Geração do tasks.yaml da Quântica a partir da Agent-Task Spec
 * de hoje (9e396ed7..., com 15 tasks vinculadas aos 15 agentes).
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Gerar tasks.yaml Quântica (Etapa 4c)', async ({ page }) => {
  test.setTimeout(2400_000);

  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  await page.goto(`${APP}/project/${PROJECT_ID}/yaml-generation`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/etapa4c-01-inicial.png`, fullPage: true });

  // Muda pra aba "Tasks YAML"
  const abaTasks = page.locator('button:has-text("Tasks YAML")').first();
  await abaTasks.click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4c-02-aba-tasks.png`, fullPage: true });
  console.log('[2] aba Tasks YAML aberta');

  // Botão Doc MD
  const docBtn = page.locator('button:has-text("Doc MD")').first();
  await docBtn.click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4c-03-modal.png`, fullPage: true });

  // Clica em "Clique para ver versões →" (primeira card = mais recente, 15 tasks)
  const verVersoes = page.locator('text=/Clique para ver vers/i').first();
  await verVersoes.waitFor({ state: 'visible', timeout: 10000 });
  await verVersoes.click({ force: true });
  await page.waitForTimeout(2500);

  // Versão 1
  const v1 = page.locator('text=/Versão\\s*1/').first();
  await v1.waitFor({ state: 'visible', timeout: 10000 });
  await v1.click({ force: true });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4c-04-carregada.png`, fullPage: true });
  console.log('[3] spec carregada');

  // Custom instructions
  const customArea = page.locator('textarea[placeholder*="Priorizar" i], textarea').first();
  if (await customArea.count() > 0 && await customArea.isVisible().catch(() => false)) {
    await customArea.fill('Gere um tasks.yaml com TODAS as 15 tasks especificadas no documento (T-PER-001 a T-REP-001). Cada task deve ter: description clara, expected_output específico, agent (nome snake_case correspondente ao agents.yaml - persona_manager_agent, pilar_content_manager_agent, calendar_generator_agent, content_editor_agent, content_approver_agent, theme_suggestor_agent, redactor_agent, fact_checker_agent, content_reviewer_agent, scheduler_agent, metrics_collector_agent, comment_classifier_agent, response_generator_agent, lead_identifier_agent, report_generator_agent), context (dependências), e human_input onde aplicável.');
  }
  await page.screenshot({ path: `${OUT}/etapa4c-05-instrucoes.png`, fullPage: true });

  const genBtn = page.locator('button:has-text("Gerar tasks.yaml"), button.btn-start-analysis').first();
  console.log(`  botão enabled=${await genBtn.isEnabled().catch(() => false)}`);
  await genBtn.click({ timeout: 5000 });
  console.log('[4] clicou Gerar tasks.yaml');
  await page.waitForTimeout(5000);

  // Aguarda até 20 min
  for (let i = 0; i < 180; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const busy = /⏳ Gerando|Gerando\.\.\./i.test(document.body.textContent || '');
      const hasYaml = /description:|expected_output:|agent:/.test(document.body.textContent || '');
      return { busy, hasYaml };
    });
    if (!state.busy && state.hasYaml) {
      console.log(`  ${(i+1)*10}s: tasks.yaml gerado`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (busy=${state.busy})`);
  }
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4c-06-final.png`, fullPage: true });
  console.log('[FIM]');
});
