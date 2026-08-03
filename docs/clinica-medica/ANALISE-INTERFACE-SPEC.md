# Análise + Refino da Interface na Especificação (ClinIA) — com o agente 32B

> Verificação pedida: ao concluir a Especificação, abrir cada caso de uso, checar como a **interface**
> está definida, avaliar a organização em **Cadastros + Agêntica**, e **refinar com o próprio agente
> (qwen2.5-coder-32b)** via `/refine`, iterando e registrando o retorno. Este documento alimenta o
> relatório final.

**Especificação gerada:** projeto `a3ae2f89`, sessão `bb40c57d`, v1 = 120.126 chars (~133 KB), 18 UCs.

## 1. Como a Especificação saiu (avaliação da v1)

**Pontos fortes (já estava bom):** a spec veio bem estruturada e **já organizada nas duas partes** que
o critério exige:

- **Parte de Cadastros (CRUD + banco):** UC-001 Cadastro de Pacientes, UC-011 Agenda/Disponibilidade,
  UC-013 Especialidades, UC-014 Médicos, UC-015 Pacientes, UC-016 Atendimentos/Triagens,
  UC-017 Pré-diagnósticos, UC-018 Encaminhamentos.
- **Parte Agêntica (atendimento):** UC-002 Triagem Agentiva, UC-003 Pré-atendimento por Especialista,
  UC-004 Geração de Pré-diagnóstico, UC-005 Agente de Encaminhamento, UC-006 Registro/Prontuário,
  UC-007 Consulta Médica, UC-009 Fallback Manual, UC-010 Visualização de KPIs.
- Cada UC tem tabela completa (atores, objetivo, pré/pós, FR/BR), Fluxo Principal/Alternativo/Exceção
  e **Wireframe ASCII**. Há a seção "7. Interfaces do Sistema" com telas de Recepção, Triagem e
  Pré-atendimento.

## 2. Lacunas de interface encontradas (o que mandei corrigir)

| # | Onde | Problema | Correção pedida ao 32B |
|---|---|---|---|
| 1 | Telas CRUD (UC-001/013/014/015/016/017/018/011) | Wireframe mostra só o **formulário**, ou uma lista em *bullets* com botões genéricos "Cadastrar/Editar/Excluir" — não é o "acesso real às informações" | Wireframe deve ter **tabela com busca + colunas reais + ações por linha (Ver/Editar/Excluir)** E o formulário Salvar/Cancelar |
| 2 | Telas agênticas (UC-002/003/004/005) | Wireframe mostra só o **resultado pré-preenchido** (ex.: "Classificação: Verde") — sem entrada nem ação | Separar **Entrada (editável) → Ação explícita ([Classificar com IA]) → Resultado do agente (classificação + área roteada) → próxima ação ([Encaminhar…])**, indicando qual agente dispara |
| 3 | Seção 7 (Interfaces) | Telas listadas soltas | Agrupar em **"Módulo de Cadastros"** e **"Módulo de Atendimento Agêntico"** para guiar a navegação por módulos |

Exemplos concretos observados na v1:
- **UC-002 Triagem** (agêntica): o wireframe já vinha com `Classificação: Verde` e `Justificativa`
  preenchidos, mas sem campo de entrada da queixa nem botão de "Classificar com IA" nem a área de
  destino roteada + botão de encaminhar.
- **UC-013 Especialidades** (CRUD): lista em bullets (`- Cardiologia (Ativa)`) + botões genéricos +
  um `[Selecionar]`, em vez de tabela com linhas e ações por linha.
- **UC-001 Cadastro de Pacientes**: só o formulário, sem a listagem dos pacientes já cadastrados.

## 3. Refino enviado ao 32B (rodada 1)

Mensagem completa em `refino-interface-01.txt`. Enviada via `POST /api/specifications/{sid}/refine`
(action_type=refine) — **aceita (HTTP 200)**, agente processando (v1→v2). Regras 1/2/3 acima.

**Resultado da rodada 1:** _(a preencher quando a nova versão sair — tamanho, e se os wireframes
passaram a ter tabela+ações nas telas CRUD e entrada+ação+resultado nas agênticas)._
