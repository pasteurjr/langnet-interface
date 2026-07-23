import { test } from '@playwright/test';
const OUT='/tmp/uso-solo-pipeline/shots-f0';
async function shoot(page, name){ await page.waitForTimeout(1800); await page.screenshot({path:`${OUT}/${name}.png`, fullPage:false}); console.log('[shot]',name); }
test('app gerado', async ({ page }) => {
  test.setTimeout(150000);
  await page.setViewportSize({ width: 1500, height: 950 });
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(3500);
  await shoot(page,'01-home-crud');           // tabela CRUD com dados reais
  // abre o form "+ Novo"
  await page.getByText('+ Novo', {exact:false}).first().click().catch(()=>{});
  await shoot(page,'02-form-novo-persona');
  // tela de permissões (fix: agora tem botão)
  await page.getByText('Gerenciamento de Permissões', {exact:false}).first().click().catch(()=>{});
  await shoot(page,'03-permissoes-com-botao');
  // uma tela de agente (IA)
  await page.getByText('Geração Automática de Conteúdo', {exact:false}).first().click().catch(()=>{});
  await shoot(page,'04-tela-agente-ia');
  // procura aba Admin / Petri
  for (const t of ['Admin','⚙','Petri','Executor','Operação']) {
    const el = page.getByText(t, {exact:false}).first();
    if (await el.count().catch(()=>0)) { await el.click().catch(()=>{}); break; }
  }
  await shoot(page,'05-admin-petri');
});
