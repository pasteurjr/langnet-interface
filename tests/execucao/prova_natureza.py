"""
Caso de teste — a separação entre função convencional e tarefa de agente.

PROVA que a regra está declarada em TODOS os pontos onde a separação tem de
existir, e que a instrução que causou o estrago foi removida.

O estrago: no BioByte, 33 casos de uso viraram 45 tarefas de agente — login,
cadastro, auditoria, envio de e-mail e até "verificar se a comunicação usa
HTTPS" ganharam um agente. Só 8 eram agênticas de verdade.

Uso:  python tests/execucao/prova_natureza.py
"""
import pathlib, sys, yaml

RAIZ = pathlib.Path(__file__).resolve().parents[2]
res = []

def confere(nome, ok, detalhe=""):
    res.append(ok)
    print(f"  {'passou' if ok else 'FALHOU'}  {nome}" + ("" if ok or not detalhe else f"\n          {detalhe}"))

# 1. os requisitos pedem a classificação
tarefas = yaml.safe_load((RAIZ / "backend/config/langnet_tasks.yaml").read_text(encoding="utf-8"))
extrai = tarefas["extract_requirements"]
confere("1. a extração de requisitos exige o campo natureza",
        "natureza" in extrai["expected_output"] and "decisao_do_agente" in extrai["expected_output"],
        "o modelo não vai devolver a marca se ninguém pedir")
confere("2. a extração explica o critério (convencional x agêntica)",
        "REGRA DE NATUREZA" in extrai["description"]
        and "convencional" in extrai["description"] and "agentica" in extrai["description"])
confere("3. a extração avisa que a MAIORIA é convencional",
        "MAIORIA seja convencional" in extrai["description"],
        "sem esse aviso o modelo tende a marcar tudo como agêntico")

# 2. o caso de uso declara a natureza
spec = (RAIZ / "backend/app/templates/specification_prompt.py").read_text(encoding="utf-8")
confere("4. a ficha do caso de uso tem o campo Natureza",
        "**Natureza**" in spec and "**Decisão do Agente**" in spec)
confere("5. o caso de uso traz o teste prático de classificação",
        "um programa comum, sem modelo de linguagem" in spec)

# 3. o portão: só o agêntico vira tarefa
ats = (RAIZ / "backend/prompts/agent_task_spec_prompt.py").read_text(encoding="utf-8")
confere("6. a instrução que mandava criar tarefa para TODO caso de uso foi REMOVIDA",
        "um UC sem task é ERRO" not in ats and "PELO MENOS UMA task\npara CADA UC" not in ats,
        "era esta a causa: obrigava uma tarefa por caso de uso")
confere("7. o portão manda NÃO gerar tarefa para caso de uso convencional",
        "Natureza = convencional" in ats and "NÃO gere tarefa" in ats)
confere("8. o portão lista o que nunca vira tarefa",
        all(x in ats for x in ["login e sessão", "cadastrar/alterar/listar/apagar",
                               "gravar auditoria", "verificar configuração"]))
confere("9. o portão trata erro como caminho de exceção, não como tarefa",
        "**caminho de exceção DENTRO** da tarefa que falhou" in ats)
confere("10. o portão manda revisar se passar de um terço dos casos de uso",
        "um terço dos casos de uso" in ats)

# 4. o documento mostra a marca
ger = (RAIZ / "backend/agents/langnetagents.py").read_text(encoding="utf-8")
confere("11. o documento de requisitos exibe a coluna Natureza",
        "| ID | Origem | Natureza | Nome |" in ger)
confere("12. requisito sem classificação aparece como não classificado, não escondido",
        "não classificado" in ger)

ok = sum(res)
print(f"\n  {ok} de {len(res)} casos passaram, {len(res)-ok} falharam")
sys.exit(0 if ok == len(res) else 1)
