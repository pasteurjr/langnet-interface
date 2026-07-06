/**
 * Refino real de requirements do Uso do Solo — abre o painel, envia 2
 * sugestões concretas, aguarda o R1 local processar, captura antes/depois.
 */
import { test, expect } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/uso-solo';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const EXEC_ID = '197e89af-c360-4f0a-bee9-5ad767381e22';

const SUGESTOES = `Aplique estas 2 modificações concretas ao Documento de Requisitos:

1) Adicione um novo FR-030 na seção 3 (Requisitos Funcionais) chamado
   "Conformidade LGPD": O sistema deve implementar controles de LGPD para
   dados pessoais coletados (proprietários, requerentes, técnicos).
   Requisitos: consentimento explícito no cadastro, direito ao esquecimento,
   base legal documentada por categoria, criptografia em repouso para CPF/CNPJ,
   log de acesso a dados sensíveis com retenção de 5 anos.
   Prioridade: Alta. Origem: Legal/Compliance.

2) Adicione um novo NFR-011 na seção 4 (Requisitos Não-Funcionais) chamado
   "SLA e Performance": SLA de disponibilidade 99.5% mensal. Tempo de
   resposta P95: consulta de área simples <=3s, geração de laudo completo
   <=30s. Deve suportar 200 consultas simultâneas sem degradação.
   Rota crítica (mapa+consulta) deve funcionar em modo offline degradado
   usando cache local por até 24h.

Atualize também a seção 19 (Controle de Versões) adicionando entrada v1.1
com as mudanças descritas. Mantenha o resto do documento intacto.`;

test('Refino Uso do Solo via UI real', async ({ page }) => {
  test.setTimeout(2400_000); // 40 min pra R1 local
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  await page.goto(`${APP}/project/${PROJECT_ID}/requirements/${EXEC_ID}`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/v2-01-antes.png`, fullPage: true });
  const antesChars = await page.evaluate(() => (document.querySelector('.markdown-container')?.textContent || '').length);
  console.log(`[2] doc carregado (${antesChars} chars)`);

  // Abre painel
  await page.locator('button:has-text("Refine with Agent")').click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/v2-02-painel-aberto.png`, fullPage: true });
  console.log('[3] painel aberto');

  // Preenche
  const ta = page.locator('.refine-textarea');
  await ta.click();
  await ta.fill(SUGESTOES);
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/v2-03-sugestoes.png`, fullPage: true });
  console.log('[4] sugestões preenchidas');

  // Envia
  await page.locator('.btn-submit-refine').click();
  console.log('[5] enviado - aguardando R1 processar...');

  // Aguarda até 25 min por feedback de sucesso ou erro
  let done = false;
  for (let i = 0; i < 150; i++) { // 150 × 10s = 25 min
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const fb = document.querySelector('.refine-feedback')?.textContent || '';
      const btn = document.querySelector('.btn-submit-refine') as HTMLButtonElement | null;
      return {
        feedback: fb,
        buttonEnabled: btn ? !btn.disabled : false,
        buttonLabel: btn?.textContent || '',
      };
    });
    if (state.feedback.startsWith('✓') || state.feedback.startsWith('✗')) {
      done = true;
      console.log(`  ${(i+1)*10}s: ${state.feedback}`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: btn="${state.buttonLabel}" fb="${state.feedback.slice(0,80)}"`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/v2-04-depois.png`, fullPage: true });

  // Compara
  const depoisText = await page.evaluate(() => (document.querySelector('.markdown-container')?.textContent || ''));
  console.log(`[6] depois: ${depoisText.length} chars`);
  const hasFR030 = depoisText.includes('FR-030');
  const hasNFR011 = depoisText.includes('NFR-011');
  const hasLGPD = depoisText.includes('LGPD');
  console.log(`  FR-030: ${hasFR030}, NFR-011: ${hasNFR011}, LGPD: ${hasLGPD}`);

  fs.writeFileSync(`${OUT}/v2-comparison.json`, JSON.stringify({
    antesChars,
    depoisChars: depoisText.length,
    hasFR030,
    hasNFR011,
    hasLGPD,
    done,
  }, null, 2));

  console.log('\n=== RESUMO ===');
  console.log(`  antes: ${antesChars} chars`);
  console.log(`  depois: ${depoisText.length} chars`);
  console.log(`  FR-030 presente: ${hasFR030}`);
  console.log(`  NFR-011 presente: ${hasNFR011}`);
});
