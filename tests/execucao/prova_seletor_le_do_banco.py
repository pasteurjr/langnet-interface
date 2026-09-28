"""Campo que aponta para outra tabela busca a lista NO BANCO, não em exemplo.

A Especificação de Interface traz opções ilustrativas ("CASO-2024-0148 — Hemocultura ·
Leito UTI-07"). Emitidas como estão, o operador escolhe um registro que não existe e o
agente responde, com razão, que não o encontrou. Medido no BioByte v5 em 28/09/2026:
nenhuma tarefa de IA conseguia trabalhar pela tela porque o caso escolhido nunca batia.
"""
import sys, os
raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, raiz + "/backend")
from agents.langnetagents import _tabela_da_chave_estrangeira as tab, _componentes_jsx as comp

DDL = """
CREATE TABLE `casos_clinicos` (`id` CHAR(36) PRIMARY KEY, `paciente_id` CHAR(36) NOT NULL,
  FOREIGN KEY (`paciente_id`) REFERENCES `pacientes`(`id`));
CREATE TABLE `pacientes` (`id` CHAR(36) PRIMARY KEY, `nome` VARCHAR(200));
CREATE TABLE `classificacoes` (`id` CHAR(36) PRIMARY KEY, `caso_id` CHAR(36),
  FOREIGN KEY (`caso_id`) REFERENCES `casos_clinicos`(`id`));
"""
falhas = []
if tab("caso_id", DDL) != "casos_clinicos":
    falhas.append(f"caso_id devia apontar para casos_clinicos, apontou {tab('caso_id', DDL)}")
if tab("paciente_id", DDL) != "pacientes":
    falhas.append("paciente_id nao achou pacientes")
if tab("resultado", DDL) is not None:
    falhas.append("campo que NAO e chave estrangeira foi tratado como se fosse")
if tab("desconhecido_id", DDL) is not None:
    falhas.append("inventou tabela para campo sem correspondencia")

COMPS = [{"type": "select", "field": "caso_id", "label": "Caso clínico",
          "options": ["CASO-2024-0148 — exemplo", "CASO-2024-0152 — exemplo"]},
         {"type": "select", "field": "resultado", "label": "Resultado",
          "options": ["sensivel", "intermediario", "resistente"]}]
jsx, _g, _u, fks = comp(COMPS, "Executar", DDL)
if ("caso_id", "casos_clinicos") not in fks:
    falhas.append(f"o campo de chave estrangeira nao foi reportado: {fks}")
if "CASO-2024-0148" in jsx:
    falhas.append("o exemplo ilustrativo continuou na tela")
if "opcoesDe[\"caso_id\"]" not in jsx:
    falhas.append("a tela nao busca a lista do campo no banco")
if "resistente" not in jsx:
    falhas.append("o campo de valores fixos (enum) perdeu as opcoes")

print(f"casos: 8 | passaram: {8-len(falhas)} | falharam: {len(falhas)}")
for m in falhas: print("  X", m)
sys.exit(1 if falhas else 0)
