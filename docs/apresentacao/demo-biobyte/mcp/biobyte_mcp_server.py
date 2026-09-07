"""
BioByte Sentinela — Servidor MCP (Model Context Protocol) de integrações externas.

Expõe DUAS ferramentas que os agentes do app gerado consomem via MCP:
  - consultar_microbiologia(paciente_id): consulta hemocultura/antibiograma no LIS externo.
  - escore_risco_cox(idade, apache_ii, tipo_cateter): serviço externo que calcula o escore de risco pelo modelo de Cox.

Transporte: SSE (compatível com o cliente MCP do backend LangNet). Porta padrão 9120.
Dados são simulados de forma realista (é a fronteira do sistema — um LIS/serviço estatístico real
plugaria aqui). Rodar:  python biobyte_mcp_server.py
"""
import os
import math
import hashlib
from typing import TypedDict, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

PORT = int(os.getenv("BIOBYTE_MCP_PORT", "9120"))
mcp = FastMCP("BioByte Sentinela - Integrações Externas", host="127.0.0.1", port=PORT)

# Banco simulado de microbiologia do LIS (por paciente).
_LIS = {
    "CAS-2023-001": {
        "id_amostra": "HMC-88213",
        "fonte": "hemocultura",
        "microrganismo": "Staphylococcus aureus",
        "multirresistente": True,   # MRSA
        "sensibilidades": {"oxacilina": "R", "vancomicina": "S", "gentamicina": "R", "clindamicina": "R"},
    },
    "CAS-2023-002": {
        "id_amostra": "HMC-88240",
        "fonte": "hemocultura",
        "microrganismo": "Escherichia coli",
        "multirresistente": False,
        "sensibilidades": {"ceftriaxona": "S", "meropenem": "S", "ciprofloxacino": "S"},
    },
}


class ResultadoMicrobiologia(TypedDict):
    # todos os campos sempre presentes (nulo quando a amostra não foi liberada) — o esquema
    # publicado pelo MCP é o que o contrato da tarefa confere
    paciente_id: str
    status: str
    id_amostra: Optional[str]
    fonte: Optional[str]
    microrganismo: Optional[str]
    multirresistente: Optional[bool]
    sensibilidades: Optional[Dict[str, str]]
    mensagem: Optional[str]


@mcp.tool()
def consultar_microbiologia(paciente_id: str) -> ResultadoMicrobiologia:
    """Consulta o resultado de hemocultura e antibiograma do paciente no sistema
    laboratorial (LIS) externo. Devolve, no vocabulário da especificação (UC-003/NHSN),
    microrganismo, sensibilidades (antibiótico -> S/I/R) e a flag de multirresistência (MDR).
    Use o identificador do caso (ex.: 'CAS-2023-001'). Amostra não liberada volta status 'pendente'."""
    reg = _LIS.get(paciente_id)
    if not reg:
        # amostra ainda não liberada pelo laboratório
        return {"paciente_id": paciente_id, "status": "pendente", "id_amostra": None, "fonte": None,
                "microrganismo": None, "multirresistente": None, "sensibilidades": None,
                "mensagem": "Hemocultura ainda não liberada pelo LIS."}
    out = {"paciente_id": paciente_id, "status": "liberado", "id_amostra": None, "fonte": None,
           "microrganismo": None, "multirresistente": None, "sensibilidades": None, "mensagem": None}
    out.update(reg)
    return out


class ResultadoCox(TypedDict):
    escore_cox: float
    nivel_risco: str
    linear_predictor: float
    fatores_de_risco: List[str]
    modelo: str


@mcp.tool()
def escore_risco_cox(idade: int, apache_ii: int, tipo_cateter: str) -> ResultadoCox:
    """Calcula o escore de risco de ICSAC pelo modelo de perigos proporcionais de Cox.
    Recebe os parâmetros clínicos que a especificação define (UC-006): idade, APACHE II e tipo
    de cateter; devolve o escore (0-1), o nível de risco (Baixo/Médio/Alto) e os fatores."""
    # Coeficientes ilustrativos do modelo de Cox (hazard ratios log-lineares).
    tc = (tipo_cateter or "").strip().lower()
    peso_cateter = (0.85 if ("dial" in tc or "hemod" in tc) else
                    0.62 if ("central" in tc or "cvc" in tc or "venoso" in tc) else
                    0.35 if "picc" in tc else 0.0)
    lp = (0.018 * max(0, float(idade) - 40)
          + 0.055 * float(apache_ii)
          + peso_cateter)
    # baseline de sobrevida acumulada -> risco = 1 - S0^exp(lp)
    S0 = 0.97
    escore = round(1.0 - math.pow(S0, math.exp(lp)), 4)
    escore = max(0.0, min(1.0, escore))
    nivel = "Alto" if escore >= 0.66 else ("Médio" if escore >= 0.33 else "Baixo")
    fatores = []
    if idade > 65: fatores.append("Idade > 65")
    if apache_ii >= 20: fatores.append(f"APACHE II elevado ({apache_ii})")
    if peso_cateter >= 0.6: fatores.append(f"Cateter de alto risco ({tipo_cateter})")
    return {"escore_cox": escore, "nivel_risco": nivel, "linear_predictor": round(lp, 4),
            "fatores_de_risco": fatores, "modelo": "Cox proportional hazards"}


if __name__ == "__main__":
    print(f"[BioByte MCP] SSE em http://127.0.0.1:{PORT}/sse  — tools: consultar_microbiologia, escore_risco_cox")
    mcp.run(transport="sse")
