/**
 * Etapa 1 do pipeline LangNet — Requirements da Quântica Comercial.
 * Loga, abre o doc, dispara refino via UI (Qwen2.5-coder-32b local),
 * aguarda, captura antes/depois pra relatório em PDF.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const EXEC_ID = '9670f599-c0f3-40d2-bb4f-8f989198f082';

const SUGESTOES = `Aplique estas 4 melhorias concretas ao Documento de Requisitos.
NÃO omita nem resuma o restante do documento — preserve integralmente.

1) Complete a Seção 7 (Entidades e Relacionamentos). Hoje ela está truncada:
   contém apenas um diagrama Mermaid iniciado (Persona ||--o{ Calendario :)
   sem terminar. Reescreva o diagrama Mermaid completo cobrindo TODAS as
   entidades identificadas nos FRs: Persona, PilarConteudo, Calendario,
   Post, ApresentacaoConteudo, ContentBrief, Lead, Empresa, Contato,
   Interacao, Aprovacao, MetricaEngajamento, e seus relacionamentos com
   cardinalidades corretas. Adicione também as subseções 7.2 (Dicionário
   de Entidades - lista tabular com nome, descrição, atributos-chave) e
   7.3 (Regras de Integridade - constraints entre entidades).

2) Acrescente a Seção 8 "Fluxos de Trabalho Identificados". Detalhe pelo
   menos 4 fluxos principais em texto + diagrama Mermaid (sequenceDiagram
   ou flowchart): (a) Fluxo Editorial (planejamento → aprovação →
   publicação), (b) Fluxo de Prospecção Outbound (identificação de leads
   → enriquecimento → cadência), (c) Fluxo de Revisão de Conteúdo por IA,
   (d) Fluxo de Aprovação do CEO.

3) Acrescente a Seção 9 "Glossário de Termos do Domínio". Inclua
   definições concisas para: Persona, Pilar de Conteúdo, Cadência,
   Ativação, ICP (Ideal Customer Profile), Lead Qualificado, Objeção,
   Gatilho de Compra, Tom de Voz, Grade Editorial, Engajamento, e outros
   termos-chave que aparecem repetidamente nos FRs.

4) Acrescente a Seção 10 "Restrições, Premissas e Dependências Externas":
   liste explicitamente restrições legais (LGPD para leads coletados),
   premissas técnicas (uso de APIs LinkedIn/Instagram — limites de rate),
   dependências de dados externos (base de contatos, enrichment via
   Apollo/Lusha), e restrições operacionais (aprovações CEO obrigatórias
   em pontos-chave — impacta SLA).

Atualize a versão do documento para 1.1 nos metadados e mantenha TODO o
conteúdo original das seções 1-6 intacto.`;

test('Refino Requisitos Quântica Comercial via UI', async ({ page }) => {
  test.setTimeout(2400_000); // 40 min pra coder local

  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');
  await page.screenshot({ path: `${OUT}/01-login.png`, fullPage: true });

  // Navega para o projeto (dashboard)
  await page.goto(`${APP}/projects`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/02-projetos.png`, fullPage: true });

  // Abre a página de requirements
  await page.goto(`${APP}/project/${PROJECT_ID}/requirements/${EXEC_ID}`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/03-requirements-antes.png`, fullPage: true });
  const antesChars = await page.evaluate(() => (document.querySelector('.markdown-container')?.textContent || '').length);
  console.log(`[2] requirements carregado - ${antesChars} chars`);

  // req-antes.md é copiado direto do banco (sem depender de token do localStorage)

  // Abre o painel Refine
  await page.locator('button:has-text("Refine with Agent")').click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/04-painel-refine.png`, fullPage: true });
  console.log('[3] painel refino aberto');

  // Preenche
  const ta = page.locator('.refine-textarea');
  await ta.click();
  await ta.fill(SUGESTOES);
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/05-sugestoes-preenchidas.png`, fullPage: true });
  console.log('[4] sugestões preenchidas');

  // Envia
  await page.locator('.btn-submit-refine').click();
  console.log('[5] enviado - aguardando coder-32b processar (pode levar 20-30 min)');

  // Poll feedback
  let done = false;
  for (let i = 0; i < 240; i++) { // 240 × 10s = 40 min
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const fb = document.querySelector('.refine-feedback')?.textContent || '';
      const btn = document.querySelector('.btn-submit-refine') as HTMLButtonElement | null;
      return { feedback: fb, buttonLabel: btn?.textContent || '' };
    });
    if (state.feedback.startsWith('✓') || state.feedback.startsWith('✗')) {
      done = true;
      console.log(`  ${(i+1)*10}s: ${state.feedback}`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: btn=${state.buttonLabel} fb=${state.feedback.slice(0,60)}`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/06-refinado.png`, fullPage: true });

  // req-depois.md será copiado do banco após teste (fora do playwright)
  console.log('[6] refino concluído');
});
