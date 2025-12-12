CORREÇÃO: Erro FK no Refinamento de Especificação

 PROBLEMA

 Erro ao refinar especificação:
 Cannot add or update a child row: a foreign key constraint fails
 (`langnet`.`chat_messages`, CONSTRAINT `fk_chat_messages_session_id`
 FOREIGN KEY (`session_id`) REFERENCES `execution_sessions` (`id`)

 CAUSA

 - chat_messages.session_id tem FK para execution_sessions
 - Especificações usam execution_specification_sessions (tabela diferente)
 - ID da especificação não existe em execution_sessions

 SOLUÇÃO

 Criar tabela specification_chat_messages com FK correta para execution_specification_sessions

 ARQUIVOS A MODIFICAR

 1. backend/database/migrations/ - criar nova migration
 2. backend/app/database.py - função save_specification_chat_message
 3. backend/app/routers/specification.py - usar nova função

 ---
 AVALIAÇÃO E MELHORIA: Documento de Especificação Gerado

 ✅ STATUS: IMPLEMENTAÇÃO CONCLUÍDA

 Todas as correções foram implementadas:
 - max_tokens=8192 configurado em backend/app/llm.py
 - backend/app/routers/specification.py atualizado (usa default max_tokens)
 - Função validate_specification_completeness() adicionada
 - Prompt de Casos de Uso melhorado em specification_prompt.py

 Próximo passo: Testar geração de especificação através da interface web

 ---
 AVALIAÇÃO DO DOCUMENTO GERADO (especificacao.md)

 Estrutura Esperada pelo Template (14 seções):

 | #   | Seção Esperada                    | Status          | Observação                                 |
 |-----|-----------------------------------|-----------------|--------------------------------------------|
 | 1   | Introdução                        | ✅ OK            | Completa                                   |
 | 2   | Visão Geral do Sistema            | ✅ OK            | Completa                                   |
 | 3   | Requisitos Funcionais Detalhados  | ⚠️ INCOMPLETO   | Só RF-001 a RF-009, faltam RF-010 a RF-024 |
 | 4   | Requisitos Não-Funcionais         | ⚠️ DESLOCADO    | Está como seção 6, simplificado            |
 | 5   | Casos de Uso                      | ⚠️ INCOMPLETO   | Só 6 UCs, sem detalhamento solicitado      |
 | 6   | Modelo de Dados Conceitual        | ⚠️ SIMPLIFICADO | Está como seção 8, falta detalhamento      |
 | 7   | Interfaces do Sistema             | ⚠️ SIMPLIFICADO | Está como seção 7                          |
 | 8   | Regras de Negócio (RN-XXX)        | ❌ AUSENTE       | Nenhuma regra documentada                  |
 | 9   | Fluxos de Trabalho                | ❌ AUSENTE       | Não existe                                 |
 | 10  | Análise de Arquitetura Preliminar | ❌ AUSENTE       | Não existe                                 |
 | 11  | Controle de Qualidade             | ❌ AUSENTE       | Não existe                                 |
 | 12  | Glossário                         | ⚠️ INCOMPLETO   | Está como seção 10, só 6 termos            |
 | 13  | Rastreabilidade (Matriz)          | ❌ AUSENTE       | Não existe                                 |
 | 14  | Apêndices                         | ❌ AUSENTE       | Não existe                                 |

 Problemas Críticos Identificados:

 1. TRUNCAMENTO: Linha 257 mostra ## CONTINUAÇÃO DA ANÁLISE - PARTE 2 - o LLM foi cortado no meio
 2. SEÇÕES FALTANTES: 6 seções completamente ausentes
 3. REQUISITOS INCOMPLETOS: Só 9 de 24 requisitos detalhados
 4. CASOS DE USO RASOS: User pediu detalhamento mas são básicos
 5. SEM REGRAS DE NEGÓCIO: Nenhuma RN-XXX documentada
 6. SEM RASTREABILIDADE: Matriz de rastreabilidade ausente

 Causa Raiz:

 # specification.py:404
 specification_document = llm.complete(prompt, max_tokens=16000)

 - max_tokens=16000 insuficiente para documento de 14 seções
 - LLM cortou no meio da geração
 - Prompt pede documento COMPLETO mas não há validação

 ---
 CORREÇÕES NECESSÁRIAS

 CORREÇÃO 1: Configurar Tokens no MÁXIMO para Claude

 Arquivo: backend/app/routers/specification.py:404

 # DE:
 specification_document = llm.complete(prompt, max_tokens=16000)

 # PARA (Claude MAX - 128k context, 8192 output):
 specification_document = llm.complete(prompt, max_tokens=8192)

 Arquivo: backend/app/llm.py - Ajustar default

 # Alterar default de max_tokens no método complete():
 def complete(
     self,
     prompt: str,
     system: Optional[str] = None,
     temperature: float = 0.7,
     max_tokens: int = 8192,  # MÁXIMO para Claude
     **kwargs
 ) -> str:

 CORREÇÃO 2: Validar Completude do Documento

 Arquivo: backend/app/routers/specification.py (após linha 404)

 Adicionar função de validação:

 def validate_specification_completeness(doc: str) -> dict:
     """Verifica se todas as 14 seções estão presentes"""
     required_sections = [
         "## 1. Introdução",
         "## 2. Visão Geral",
         "## 3. Requisitos Funcionais",
         "## 4. Requisitos Não-Funcionais",
         "## 5. Casos de Uso",
         "## 6. Modelo de Dados",
         "## 7. Interfaces",
         "## 8. Regras de Negócio",
         "## 9. Fluxos de Trabalho",
         "## 10. Análise de Arquitetura",
         "## 11. Controle de Qualidade",
         "## 12. Glossário",
         "## 13. Rastreabilidade",
         "## 14. Apêndices"
     ]

     missing = []
     for section in required_sections:
         if section.lower() not in doc.lower():
             missing.append(section)

     return {
         "complete": len(missing) == 0,
         "missing_sections": missing,
         "section_count": 14 - len(missing)
     }

 CORREÇÃO 3: Geração Multi-Passo (Opcional mas Recomendado)

 Se mesmo com 32k tokens ainda truncar, implementar geração por seção:

 async def generate_specification_multi_pass(requirements_doc, ...):
     sections = []

     # Gerar seções em grupos
     section_groups = [
         ["1. Introdução", "2. Visão Geral", "3. Requisitos Funcionais"],
         ["4. RNF", "5. Casos de Uso Detalhados"],
         ["6. Modelo de Dados", "7. Interfaces", "8. Regras de Negócio"],
         ["9. Fluxos", "10. Arquitetura", "11. Qualidade"],
         ["12. Glossário", "13. Rastreabilidade", "14. Apêndices"]
     ]

     for group in section_groups:
         prompt = build_section_prompt(requirements_doc, group)
         section_content = llm.complete(prompt, max_tokens=8000)
         sections.append(section_content)

     return "\n\n".join(sections)

 CORREÇÃO 4: Melhorar Prompt para Casos de Uso Detalhados

 Arquivo: backend/app/templates/specification_prompt.py

 Na seção de Casos de Uso, adicionar instrução mais específica:

 ## 5. Casos de Uso

 ### INSTRUÇÕES CRÍTICAS PARA CASOS DE USO:
 1. Criar um UC para CADA requisito funcional principal
 2. CADA UC deve ter NO MÍNIMO:
    - 5-10 passos no fluxo principal
    - 2-3 fluxos alternativos
    - 2-3 fluxos de exceção
    - Pré-condições e pós-condições detalhadas
 3. NÃO resumir - detalhar cada passo com ações específicas
 4. Incluir interações de UI quando aplicável
 5. Referenciar TODOS os RFs relacionados

 ---
 ARQUIVOS A MODIFICAR

 1. backend/app/routers/specification.py
   - Linha 404: Aumentar max_tokens para 32000
   - Adicionar função validate_specification_completeness()
   - Adicionar log de validação após geração
 2. backend/app/templates/specification_prompt.py
   - Reforçar instruções para Casos de Uso detalhados
   - Adicionar contagem mínima de seções
   - Enfatizar que TODAS as 14 seções são OBRIGATÓRIAS
 3. backend/app/llm.py (opcional)
   - Verificar se provider suporta 32k tokens
   - Adicionar fallback para geração multi-passo

 ---
 ORDEM DE EXECUÇÃO

 1. Aumentar max_tokens em specification.py
 2. Adicionar validação de completude
 3. Melhorar instruções de Casos de Uso no template
 4. Regenerar especificação e validar
 5. Se ainda truncar, implementar geração multi-passo

 ---
 RESUMO DO PROBLEMA

 O documento gerado está INCOMPLETO porque:
 - LLM cortou a geração por limite de tokens
 - 6 das 14 seções estão ausentes
 - Casos de uso não estão detalhados como solicitado
 - Requisitos funcionais parcialmente documentados (9 de 24)

 Solução principal: Aumentar max_tokens e adicionar validação de completude.