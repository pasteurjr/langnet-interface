IDENTIFIQUEI O PROBLEMA!

  O erro acontece porque existe uma FOREIGN KEY constraint:
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)

  O project_id que você está enviando NÃO EXISTE na tabela projects. Os projetos válidos são:
  - ce0b4082-7ad0-4e1e-b0b9-a76846ffa76f - Assistente de Atendimento
  - a62c0d72-89f3-4cca-9da2-5a88867cd32e - Gerenciador de Editais
  - c0a28a75-f050-4d49-ac9d-49628efeb964 - Projeto Teste API
  - 9a2c56de-ada5-4c49-b4a5-29bc237a590a - Sistema de Processamento de Emails

  Mas você enviou: 4a6550af-c3d5-11f0-8a15-cae41bd7e6fb (que não existe!)

  📋 Plano de Correção:

  1. Adicionar validação do project_id antes do INSERT
  2. Retornar erro claro se o projeto não existir
  3. Verificar de onde vem esse project_id no frontend

  Vou implementar isso agora:
  ⎿  User rejected Claude's plan:
     ╭────────────────────────────────────────────────────────────────────────────────────╮
     │ Correção do Erro de Upload de Documentos                                           │
     │                                                                                    │
     │ Problema Identificado                                                              │
     │                                                                                    │
     │ O erro "Truncated incorrect DECIMAL value" acontece porque:                        │
     │ - A tabela documents tem FOREIGN KEY para projects(id)                             │
     │ - O project_id enviado não existe na tabela projects                               │
     │ - MySQL gera mensagem confusa sobre DECIMAL quando FK falha                        │
     │                                                                                    │
     │ Solução                                                                            │
     │                                                                                    │
     │ 1. Validar project_id Antes do INSERT                                              │
     │                                                                                    │
     │ Adicionar verificação em backend/app/routers/documents.py no endpoint /upload:     │
     │ # Validate project exists                                                          │
     │ cursor.execute("SELECT id FROM projects WHERE id = %s", (project_id,))             │
     │ if not cursor.fetchone():                                                          │
     │     raise HTTPException(status_code=404, detail=f"Project {project_id} not found") │
     │                                                                                    │
     │ 2. Melhorar Mensagens de Erro                                                      │
     │                                                                                    │
     │ Tornar erros de FK mais claros para o usuário.                                     │
     │                                                                                    │
     │ 3. Verificar Frontend                                                              │
     │                                                                                    │
     │ Checar de onde vem o project_id inválido na interface.                             │
     │                                                                                    │
     │ Arquivos a Modificar                                                               │
     │                                                                                    │
     │ - backend/app/routers/documents.py - adicionar validação                           │
     │                                                                                    │
     │ Resultado Esperado                                                                 │
     │                                                                                    │
     │ Erro claro: "Project XXX not found" em vez de "DECIMAL value"                      │
     ╰────────────────────────────────────────────────────────────────────────────────────╯
✅ CONCLUÍDO (Fases 1-3):

  1. ✅ WebSocket autenticado - Frontend e backend prontos
  2. ✅ Integração LangNet - Análise real de documentos funcionando
  3. ✅ Salvamento de documento - Requirements_document salvo no banco
  4. ✅ Endpoints GET/PUT - Buscar e editar requisitos
  5. ✅ Serviço Frontend - requirementsService.ts criado
  6. ✅ Editor conectado - MarkdownEditorModal salva no backend

  ⏳ FALTAM (Fases 4-5):

  7. ⏳ Refinamento conversacional - Integrar chat com LangNet
  8. ⏳ PDF Server-side - Instalar weasyprint e criar endpoint
  9. ⏳ Exibir documento - Mostrar no chat após análise
  10. ⏳ Passar sessionId - Atualizar DocumentsPage

  Por questão de tamanho de contexto e para não arriscar quebrar código, vou deixar você testar primeiro o que já está funcionando e depois continuamos com as partes restantes.

  Quer que eu continue agora ou prefere testar o que já fizemos?

  Todos
  ☒ Adicionar autenticação ao WebSocket no backend
  ☒ Corrigir URL do WebSocket no frontend e adicionar token
  ☒ Adicionar coluna requirements_document na tabela execution_sessions
  ☒ Salvar documento gerado no banco após análise LangNet
  ☒ Criar endpoint GET para buscar documento de requisitos
  ☒ Criar endpoint PUT para salvar edições de requisitos
  ☒ Conectar MarkdownEditorModal ao backend para salvar edições
  ☐ Integrar refinamento conversacional com LangNet
  ☐ Instalar dependências para PDF (weasyprint, markdown)
  ☐ Criar serviço de exportação PDF server-side
  ☐ Criar endpoint POST para exportar PDF
  ☐ Conectar botão Exportar PDF ao endpoint backend
  ☐ Exibir documento gerado no chat após análise
  ☐ Testar fluxo completo end-to-end
