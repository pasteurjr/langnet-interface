"""Tools customizadas detectadas: database_tool, embedding_tool.

Esqueleto: adicione classes que herdem de crewai.tools.BaseTool conforme necessário.
"""
from database_tool import DatabaseTool, database_tool
from typing import Any
from crewai.tools import BaseTool


# (Sem tools customizadas detectadas — adicione conforme necessário.)


# ─── Registro automático de tools (best-effort) ───
try:
    TOOL_REGISTRY = {
        'database_tool': None,  # TODO: classe DatabaseTool não detectada no tools.py
        'embedding_tool': None,  # TODO: classe EmbeddingTool não detectada no tools.py
    }
    TOOL_REGISTRY = {k: v for k, v in TOOL_REGISTRY.items() if v is not None}
except Exception as _e:
    TOOL_REGISTRY = {}
    print(f'[tools] WARN: TOOL_REGISTRY skeleton falhou: {_e}')

# LangNet: tools locais REAIS (substituem quaisquer mocks) — ver tools_std.py
try:
    from tools_std import STD_TOOLS as _STD_TOOLS
    TOOL_REGISTRY.update(_STD_TOOLS)
except Exception as _e:
    print(f'[tools] WARN: tools_std indisponível: {_e}')

# LangNet: integrações externas (config via .env) — ver tools_ext.py
try:
    from tools_ext import EXT_TOOLS as _EXT_TOOLS
    TOOL_REGISTRY.update(_EXT_TOOLS)
except Exception as _e:
    print(f'[tools] WARN: tools_ext indisponível: {_e}')
