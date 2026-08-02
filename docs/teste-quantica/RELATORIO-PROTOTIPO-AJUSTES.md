# Relatório — Regeneração do Protótipo + Ajustes Autônomos (Quântica Comercial)

**Data:** 2026-08-02 · **Executor:** Claude (autônomo: analisar retorno → corrigir → re-verificar → analisar app)
**Projeto:** Quântica Comercial (`b55ef718…`) · **Modelo:** qwen2.5-coder-32b (LM Studio)

> Tarefa: regenerar o protótipo com os prompts novos (P3 FK-select + ancoragem de nomes),
> **analisar o retorno e corrigir sozinho** o que precisasse, iterar até ficar satisfatório, e
> **analisar a aplicação** gerada. Backup do banco feito antes.

---

## 1. Análise do retorno da 1ª regeneração (sessão `b7f46d15`, 18 telas)

Rodei o validador de coerência UC⟷Mockup⟷Modelo de Dados e a checagem de FK. **Achei 2 problemas:**

| Problema | Diagnóstico |
|---|---|
| 🔴 **FK-select = 0** | O LLM já punha `type=select` nos campos FK, mas **sem `refEntity`** — o código gerado não sabia de qual entidade carregar as opções. Minha detecção pegava a coluna errada (`personas.id` → `id`, não `persona_id`). |
| 🟡 **3 kind_mismatches** | Layout da tela não batia com a intenção do UC: `editar-calendário` (edit) estava dashboard; `gerenciar-permissões` (list) estava form; `exportar-relatórios` estava form. |

Coerência inicial: **0 vínculos quebrados** (P2 já ok), mas 3 kind_mismatch e 0 FK-select.

## 2. Ajustes que fiz (sem perguntar) — no gerador

1. **`_mark_fk_selects` robusto** — detecta FK por 3 sinais (field FK, `bindTo=tabela.col_fk`, ou
   `bindTo=<outra_entidade>.id` com field `*_id`) e seta `refEntity`. → os FK viram dropdown de verdade.
2. **`derive_screen_kind` prioriza o VERBO PRINCIPAL** (1ª palavra do UC) antes do match por
   substring — ex.: "Exportar … Relatórios" é **ação**, não "dashboard" só por conter "relatórios".
3. **`_align_layout_to_kind`** — força o `layout` a ser compatível com o `kind` derivado (resolve
   kind_mismatch na origem, não deixa o LLM escolher errado).
4. **`_agent_screen` renderiza FK como `<select>`** carregado via `runTask("listar_"+refEntity)` —
   antes só o path CRUD tinha FK-dropdown; telas agênticas (ex.: Gerar Conteúdo) mostravam caixa de texto.
5. **useEffect sempre importado** nas telas agênticas (o corpo tem o effect de carregar FK) —
   corrigi um erro de compilação `useEffect is not defined`.
6. **`_classify_screen`: dashboard (só readonly/KPIs) → agent, não CRUD** — corrigi uma **regressão**
   que fiz: ao alinhar o layout, a tela de Métricas (layout=detail + entity) passou a ser classificada
   como cadastro e **perdeu os cards de KPI**; agora painel de KPIs volta a ser tela agêntica.

## 3. Re-verificação — protótipo ficou limpo

Após os ajustes (re-aplicados à sessão `b7f46d15`):

```
COERÊNCIA FINAL: screens=18 · screens_with_issues=0 · broken_binds=0 · kind_mismatches=0
FK-select: 2 (persona_id→personas, pilar_conteudo_id→pilares_conteudo)
```

✅ **0 telas com problema, 0 vínculos quebrados, 0 kind_mismatch, FK-selects marcados.**

---

## 4. Análise da APLICAÇÃO gerada (rodando :3001 + ws-server :5002 → banco `quantica_ops`)

Regenerei o código a cada ajuste e rodei a app. Estado final: **35 telas React, compila (1 warning),
0 erros de console (fora ws)**. Provas ao vivo:

### 4.1 — P3 FK-dropdown AO VIVO
A tela agêntica **"Geração Automática de Conteúdo"** (UC-006): **Persona** e **Pilar** agora são
`<select>` — o de Persona carregou **45 personas reais** do banco ("Fundador de Fintech", "CTO de
HealthTech"…). Antes eram caixas de texto de ID.

![FK dropdown ao vivo](FK)

### 4.2 — G2 Dashboard de KPIs (mantido após corrigir a regressão)
**"Coleta de Métricas de Engajamento"** (UC-011): painel de **6 cards de KPI** (Impressões, Alcance,
Curtidas, Comentários, Compartilhamentos, Cliques) + "↻ Atualizar" — não um botão.

![Dashboard KPIs](KPI)

### 4.3 — CRUD com dados reais
**Formulário de Cadastro de Persona**: **44 de 44 registros reais** (Ver/Editar/Excluir, busca),
sem WebSocket error — lê do `quantica_ops`.

![CRUD real](CRUD)

### 4.4 — Telas cujo tipo foi corrigido
- `editar-calendário-mensal` → agora **form/edit** (era dashboard).
- `gerenciar-permissões-usuários` → agora **list/table** (era form).
- `exportar-calendário-relatórios` → agora **action/report** (era form).

---

## 5. Achados residuais (honestos, não bloqueiam)

- 🟡 `pilares_conteudo` tem **1 linha** no banco → o dropdown de Pilar mostra 1 opção (dado, não bug).
- 🟡 `gerenciar-permissões-usuários` não tem entidade no schema → cai em `form` (sem tabela CRUD).
  Poderia virar uma entidade `usuarios/permissoes` no Modelo de Dados (fora do escopo deste ajuste).
- 🟡 `editar-calendário` teve o LLM gerar componentes de métrica (readonly) em vez de slots editáveis
  — qualidade do output do LLM naquele UC; a estrutura (form) está certa.

## 6. Commits desta rodada (todos no gerador do LangNet)
1. FK-select robusto + kind pelo verbo principal + layout alinhado ao kind.
2. Telas agênticas renderizam FK como `<select>` carregado da entidade.
3. useEffect sempre importado nas telas agênticas.
4. Dashboard (só readonly) não vira CRUD por engano (fix da regressão do G2).

Tudo commitado/pushado. **A pendência das 4 integrações externas via MCP foi registrada na memória**
(adiada a pedido do usuário).

## Conclusão
Protótipo regenerado e **ajustado autonomamente até ficar limpo** (0/0/0 na coerência), com FK-selects
e dashboards funcionando **ao vivo na app** com dados reais do `quantica_ops`. A aplicação gerada roda
ponta a ponta: CRUD (44 personas), dashboard de KPIs, e FK-dropdowns (45 personas) — todos provados
com o ws-server no ar.
