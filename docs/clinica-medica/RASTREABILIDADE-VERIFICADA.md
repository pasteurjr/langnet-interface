# Rastreabilidade Spec ⟷ Interface ⟷ Implementação — VERIFICADA

> Você pediu para eu **verificar se existe rastreabilidade** entre a Especificação (casos de uso), a
> Interface e a Implementação. **Existe** — verifiquei no código, nos endpoints e na própria UI do
> LangNet. Abaixo, o que é rastreado, a prova concreta, e o limite (registro vs propagação automática).

## 1. O que existe (comprovado)

### a) Proveniência versionada (registro da fonte)
Cada etapa **grava de qual versão da spec (e das outras fontes) foi gerada** (migrations 023–029):
- Protótipo (`ui_spec_sessions`) grava `specification_session_id` + `specification_version` (+ Modelo de Dados).
- Código (`code_generation_sessions`) grava as 4 sessões-fonte + versões + `ui_spec_session_id`/`version`.
- Casos de Teste, Modelo de Dados, Sequência, Petri — idem.

**Prova (API `sync-status` do protótipo da ClinIA):**
```
{ "spec_session_id": "bb40c57d…", "spec_version_used": 2, "spec_version_current": 2, "stale": false }
```
→ o protótipo **sabe** que veio da **spec versão 2** e compara com a atual.

### b) Amarração tela ⟷ Caso de Uso (Interface ↔ Spec)
Cada tela do protótipo carrega o **UC de origem**. Na UI (página **Interface & Protótipo**) cada tela
aparece com seu UC: *Cadastro de Pacientes → UC-001*, *Triagem Agentiva → UC-002*, *Pré-atendimento →
UC-003*, … *Gestão de Especialidades → UC-013*. E a etiqueta **"Origem: Especificação bb40c57d…"**.

**Prova (API `screen/{id}/source`):**
```
screen_id: triagem-agentiva · uc_id: UC-002 · actor/objetivo/flow/wireframe do UC · spec_version_used: 2
```
→ a tela `triagem-agentiva` está ligada ao **UC-002** e expõe o **fluxo + wireframe** daquele caso de uso.

### c) Referência do UC na Implementação (código)
Cada tela React gerada mostra o UC no **subtítulo** (ex.: "UC-002 · executado por agente de IA"),
injetado de `screen.uc`. **Fecha a cadeia:** UC-002 (Spec) → tela triagem-agentiva (Interface) →
subtítulo "UC-002" (Código React).

### d) Amarração BIDIRECIONAL (editar interface → atualiza a Spec)
Endpoint `POST /ui-spec/{sid}/screen/{id}/edit-source`: ao editar o **fluxo/wireframe** de uma tela,
o LangNet **grava uma nova versão da Especificação** (no UC) **e regenera aquela tela** — ou seja, uma
edição na interface **reflete na Especificação**. E `resync` re-sincroniza uma tela com a spec atual.

### e) Coerência UC ⟷ Mockup ⟷ Modelo de Dados
Botão **"Verificar coerência"** (endpoint `/coherence`): valida cada tela contra o schema real e o UC
(tipo de tela x intenção, binds quebrados) e **propõe** mudanças ao Modelo de Dados (aplicáveis por
`apply-dm-changes`, que cria nova versão do DM e reaponta a proveniência).

## 2. O limite importante (o que NÃO é automático)

A rastreabilidade é de **REGISTRO (proveniência) + DETECÇÃO de defasagem (staleness)**, **não** de
**propagação automática**. Quando a Especificação é refinada (nova versão), o protótipo e o código
**não se regeneram sozinhos** — o sistema apenas marca **`stale: true`** (versão usada < atual) e é
preciso **regenerar** cada etapa (ou, por tela, usar `resync`/`edit-source`). Só o par
tela⟷spec/DM tem propagação semi-automática, disparada pelo usuário, tela a tela.

**Demonstração ao vivo:** ao disparar o refino da Especificação (v2 → v3, reorganização da interface),
o `sync-status` do protótipo passa de `stale: false` para **`stale: true`** — o LangNet **detecta** que
o protótipo ficou defasado da spec. *(Prova capturada após o refino concluir.)*

## 3. Conclusão

**A rastreabilidade Especificação (UCs) ⟷ Interface (telas↔UC + proveniência) ⟷ Implementação (UC no
código) EXISTE e é verificável** — inclusive bidirecional (editar a interface atualiza a spec) e com
validação de coerência. O que **falta** é a **propagação automática** ao refinar a spec: hoje é
registro + detecção de staleness + regeneração manual. Isso é aceitável (e explícito), mas é o ponto a
evoluir se quisermos "mudou a spec → tudo se atualiza sozinho".
