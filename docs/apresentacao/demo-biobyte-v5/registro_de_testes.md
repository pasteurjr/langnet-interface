# Registro de Testes — BioByte Sentinela v5

Executado em 28/09/2026 02:25 contra a aplicação implantada (servidor de agentes na porta 5033, banco `biobyte_v5_app`).

**22 de 23 casos passaram.**

Cada caso tem um veredito conferido: no cadastro, contra a linha no banco; nos agentes, contra o gabarito plantado (uma amostra com 4 classes resistentes e outra com 1).

## Cadastro — listar, criar, ler, alterar, excluir

| | Caso | Esperado | Obtido |
|---|---|---|---|
| ✅ | pacientes · listar | a tela recebe as 3 linhas do banco | recebeu 3 |
| ✅ | pacientes · criar | o banco passa de 3 para 4 linhas | ficou com 4 (resposta: {'status': 'sucesso', 'id': 'e6021f18-bafc-11f1-8a9e-cbeb38540001', 'n) |
| ✅ | pacientes · ler | devolve o registro recém-criado | devolveu {'id': 'e6021f18-bafc-11f1-8a9e-cbeb38540001', 'nome': 'Teste CRUD', 'data_nascimento': '1 |
| ✅ | pacientes · alterar | o campo nome vira 'Teste CRUD ALTERADO' NO BANCO | no banco está 'Teste CRUD ALTERADO' |
| ✅ | pacientes · excluir | o banco volta de 4 para 3 linhas | ficou com 3 |
| ✅ | antimicrobianos · listar | a tela recebe as 6 linhas do banco | recebeu 6 |
| ✅ | antimicrobianos · criar | o banco passa de 6 para 7 linhas | ficou com 7 (resposta: {'status': 'sucesso', 'id': 'e876520e-bafc-11f1-8a9e-cbeb38540001', 'n) |
| ✅ | antimicrobianos · ler | devolve o registro recém-criado | devolveu {'id': 'e876520e-bafc-11f1-8a9e-cbeb38540001', 'nome': 'Teste-AM-e846e', 'classe': 'Classe |
| ✅ | antimicrobianos · alterar | o campo classe vira 'Classe ALTERADA' NO BANCO | no banco está 'Classe ALTERADA' |
| ✅ | antimicrobianos · excluir | o banco volta de 7 para 6 linhas | ficou com 6 |
| ✅ | bundles · listar | a tela recebe as 3 linhas do banco | recebeu 3 |
| ✅ | bundles · criar | o banco passa de 3 para 4 linhas | ficou com 4 (resposta: {'status': 'sucesso', 'id': 'eaebb634-bafc-11f1-8a9e-cbeb38540001', 'n) |
| ✅ | bundles · ler | devolve o registro recém-criado | devolveu {'id': 'eaebb634-bafc-11f1-8a9e-cbeb38540001', 'nome': 'Bundle de Teste 3642d', 'indicacao |
| ✅ | bundles · alterar | o campo indicacao vira 'indicacao ALTERADA' NO BANCO | no banco está 'indicacao ALTERADA' |
| ✅ | bundles · excluir | o banco volta de 4 para 3 linhas | ficou com 3 |

## Agentes — as cinco tarefas de inteligência artificial

| | Caso | Esperado | Obtido |
|---|---|---|---|
| ✅ | multirresistência · conta as classes (caso 4 classes) | contagem = 4 | contagem = 4.0 |
| ❌ | multirresistência · aplica a regra das três classes | multirresistente = verdadeiro | multirresistente = None |
| ✅ | multirresistência · conta as classes (caso 1 classe) | contagem = 1 | contagem = 1.0 |
| ✅ | tradução · traz o antibiograma completo do banco | 6 antimicrobianos, todos com classe | 6 antimicrobianos, 6 com classe |
| ✅ | tradução · recusa amostra inexistente sem inventar | aproveitável = falso, com justificativa | aproveitável = False, justificativa de 1727 caracteres |
| ✅ | classificação · responde pelo critério da norma | confirmada, descartada ou pendente | pendente |
| ✅ | recomendação · escolhe pacote que existe no cadastro | um pacote do cadastro, com justificativa | Bundle de precaução de contato + descalonamento (justificativa: 948 car) |
| ✅ | alerta · redige o texto citando o achado clínico | texto clínico citando o achado | 1039 caracteres, cita o achado = True |
