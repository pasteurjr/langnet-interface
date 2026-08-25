# Documento de Legislação/Norma — Estrutura do Laudo e Parecer Técnico

**Finalidade:** complementa os requisitos definindo o **documento de saída** do sistema — o **laudo de
conformidade / parecer técnico-ambiental** que o app deve **emitir** ao final da avaliação.

## Base normativa
- Práticas de **laudo de viabilidade ambiental** e **parecer técnico** (normas ABNT aplicáveis;
  responsabilidade técnica via **ART/TRT** de profissional habilitado — CREA/CFBio).
- Distinção: **laudo** = diagnóstico das condições; **parecer** = interpretação e conclusão sobre a
  viabilidade e condicionantes.

## Requisito funcional: emitir o laudo de conformidade
Ao concluir a avaliação de um imóvel/empreendimento, o sistema DEVE **gerar um laudo** com a estrutura:

1. **Identificação / Capa** — responsável técnico (nome, registro CREA/CFBio, **ART**), requerente,
   imóvel (matrícula, **coordenadas georreferenciadas**), data de emissão.
2. **Resumo executivo** — síntese e **conclusão de viabilidade**.
3. **Introdução e objetivos** — escopo e parâmetros analisados.
4. **Metodologia** — normas ABNT, **geoprocessamento** (bases utilizadas, SRID, datas).
5. **Caracterização da área** — localização georreferenciada, **zona de uso do solo** incidente,
   geologia/hidrologia, uso atual, **APP/UC incidentes**.
6. **Análise de conformidade** — para cada **parâmetro urbanístico** e **restrição ambiental**:
   valor exigido × valor do projeto → **conforme / não conforme**, com fundamentação legal.
7. **Requisitos e condicionantes** — lista de exigências (uma por regra) e documentos necessários.
8. **Conclusão** — **viável / viável com condicionantes / inviável**.
9. **Referências** — legislação citada.
10. **Anexos** — mapas, registro fotográfico, ART, certidões.

## Requisito de dados: entidade Laudo
O sistema DEVE persistir o laudo com: vínculo à **consulta**, **conclusão** (viável | condicionado |
inviável), **responsável técnico**, **ART**, **documento** (texto/relatório completo), **data de emissão**.

## Impacto no modelo de dados / tarefas
- Entidade `laudo` (consulta_id, conclusao, responsavel_tecnico, art, documento, data_emissao).
- Tarefa `emitir_laudo`: consolida caracterização + análise de conformidade + requisitos + conclusão no
  formato acima e grava em `laudo.documento`.
- Cada **requisito** deve trazer `fundamentacao_legal`, `parametro`, `valor_exigido`, `valor_projeto` e
  `situacao`, para compor a seção 6 (análise de conformidade) do laudo.
