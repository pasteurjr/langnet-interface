"""
BioByte Sentinela — Servidor MCP (Model Context Protocol) de integrações externas.

Expõe DUAS ferramentas que os agentes do app gerado consomem via MCP:
  - consultar_microbiologia(paciente_id): consulta hemocultura/antibiograma no LIS externo.
  - escore_risco_cox(...): serviço externo que calcula o escore de risco pelo modelo de Cox.

Transporte: SSE (compatível com o cliente MCP do backend LangNet). Porta padrão 9120.
Dados são simulados de forma realista (é a fronteira do sistema — um LIS/serviço estatístico real
plugaria aqui). Rodar:  python biobyte_mcp_server.py
"""
import os
import math
import hashlib
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
        "perfil_resistencia": {"oxacilina": "R", "vancomicina": "S", "gentamicina": "R"},
    },
    "CAS-2023-002": {
        "id_amostra": "HMC-88240",
        "fonte": "hemocultura",
        "microrganismo": "Escherichia coli",
        "multirresistente": False,
        "perfil_resistencia": {"ceftriaxona": "S", "meropenem": "S", "ciprofloxacino": "S"},
    },
}


@mcp.tool()
def consultar_microbiologia(paciente_id: str) -> dict:
    """Consulta o resultado de hemocultura e antibiograma do paciente no sistema
    laboratorial (LIS) externo. Retorna microrganismo, perfil de resistência e flag de
    multirresistência (MDR). Use o identificador do caso (ex.: 'CAS-2023-001')."""
    reg = _LIS.get(paciente_id)
    if not reg:
        # amostra ainda não liberada pelo laboratório
        return {"paciente_id": paciente_id, "status": "pendente",
                "mensagem": "Hemocultura ainda não liberada pelo LIS."}
    out = {"paciente_id": paciente_id, "status": "liberado"}
    out.update(reg)
    return out


@mcp.tool()
def escore_risco_cox(dias_cateter: int, uti: bool, nutricao_parenteral: bool,
                     neutropenia: bool, idade: int) -> dict:
    """Calcula o escore de risco de ICSAC pelo modelo de perigos proporcionais de Cox.
    Recebe fatores clínicos (dias de cateter, internação em UTI, nutrição parenteral,
    neutropenia, idade) e devolve o escore (0-1) e o nível de risco (Baixo/Médio/Alto)."""
    # Coeficientes ilustrativos do modelo de Cox (hazard ratios log-lineares).
    lp = (0.045 * float(dias_cateter)
          + 0.62 * (1 if uti else 0)
          + 0.48 * (1 if nutricao_parenteral else 0)
          + 0.85 * (1 if neutropenia else 0)
          + 0.018 * max(0, float(idade) - 40))
    # baseline de sobrevida acumulada -> risco = 1 - S0^exp(lp)
    S0 = 0.97
    escore = round(1.0 - math.pow(S0, math.exp(lp)), 4)
    escore = max(0.0, min(1.0, escore))
    nivel = "Alto" if escore >= 0.66 else ("Médio" if escore >= 0.33 else "Baixo")
    fatores = []
    if idade > 65: fatores.append("Idade > 65")
    if uti: fatores.append("Internação em UTI")
    if nutricao_parenteral: fatores.append("Nutrição parenteral")
    if neutropenia: fatores.append("Neutropenia")
    if dias_cateter >= 7: fatores.append(f"Cateter central há {dias_cateter} dias")
    return {"escore_cox": escore, "nivel_risco": nivel, "linear_predictor": round(lp, 4),
            "fatores_de_risco": fatores, "modelo": "Cox proportional hazards"}


if __name__ == "__main__":
    print(f"[BioByte MCP] SSE em http://127.0.0.1:{PORT}/sse  — tools: consultar_microbiologia, escore_risco_cox")
    mcp.run(transport="sse")
