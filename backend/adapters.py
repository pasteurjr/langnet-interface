import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Adaptadores de entrada (input_func) e saída (output_func) para cada task
# do sistema multi-agente. Cada função segue o padrão:
#   def TASK_input_func(state: dict) -> dict
#   def TASK_output_func(state: dict, result: Any) -> dict
# ---------------------------------------------------------------------------


def _deep_get(state: dict, *keys, default=None) -> Any:
    """Navega aninhado no dicionário state retornando o valor ou default."""
    current = state
    for k in keys:
        if isinstance(current, dict):
            current = current.get(k, default)
        else:
            return default
    return current


def _merge_outputs(state: dict, task_id: str, result: Any) -> dict:
    """Atualiza state['outputs'][task_id] com o resultado da task."""
    if 'outputs' not in state:
        state['outputs'] = {}
    state['outputs'][task_id] = result
    return state


# ============================================================================
# 1. cadastrar_persona_alvo
# ============================================================================
def cadastrar_persona_alvo_input_func(state: dict) -> dict:
    """
    Extrai dados da persona do estado anterior e retorna kwargs para a task.
    Espera que state contenha 'input_data' com os campos:
    nome, descricao, canais, problemas, gatilhos_de_compra, objecoes, palavras_chave.
    """
    input_data = state.get('input_data', {}) or state.get('previous_outputs', {}).get('P_persona_start', {})
    return {
        'nome': input_data.get('nome', ''),
        'descricao': input_data.get('descricao', ''),
        'canais': input_data.get('canais', []),
        'problemas': input_data.get('problemas', []),
        'gatilhos_de_compra': input_data.get('gatilhos_de_compra', []),
        'objecoes': input_data.get('objecoes', []),
        'palavras_chave': input_data.get('palavras_chave', []),
    }


def cadastrar_persona_alvo_output_func(state: dict, result: Any) -> dict:
    """
    Processa o resultado da task. Espera um dict com 'persona_id' e 'status'.
    Atualiza state['outputs']['cadastrar_persona_alvo'].
    """
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': 'erro', 'raw': result}
    return _merge_outputs(state, 'cadastrar_persona_alvo', result)


# ============================================================================
# 2. editar_persona_alvo
# ============================================================================
def editar_persona_alvo_input_func(state: dict) -> dict:
    """Extrai dados de edição da persona do state."""
    input_data = state.get('input_data', {}) or state.get('previous_outputs', {}).get('P_persona_start', {})
    return {
        'persona_id': input_data.get('persona_id', ''),
        'nome': input_data.get('nome', ''),
        'descricao': input_data.get('descricao', ''),
        'canais': input_data.get('canais', []),
        'problemas': input_data.get('problemas', []),
        'gatilhos_de_compra': input_data.get('gatilhos_de_compra', []),
        'objecoes': input_data.get('objecoes', []),
        'palavras_chave': input_data.get('palavras_chave', []),
    }


def editar_persona_alvo_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da edição."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': 'erro', 'raw': result}
    return _merge_outputs(state, 'editar_persona_alvo', result)


# ============================================================================
# 3. gerenciar_permissoes_usuario
# ============================================================================
def gerenciar_permissoes_usuario_input_func(state: dict) -> dict:
    """Extrai dados de permissão do state."""
    input_data = state.get('input_data', {}) or state.get('previous_outputs', {}).get('P_perm_start', {})
    return {
        'usuario_id': input_data.get('usuario_id', ''),
        'perfil': input_data.get('perfil', ''),
    }


def gerenciar_permissoes_usuario_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado do gerenciamento de permissões."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'gerenciar_permissoes_usuario', result)


# ============================================================================
# 4. gerar_calendario_mensal
# ============================================================================
def gerar_calendario_mensal_input_func(state: dict) -> dict:
    """Extrai dados para gerar calendário mensal."""
    # Pode vir de cadastrar_persona_alvo ou editar_persona_alvo (ambos têm persona_id)
    prev = state.get('previous_outputs', {})
    cad = prev.get('P_cadastrar_done', {}) or {}
    ed = prev.get('P_editar_done', {}) or {}
    input_data = state.get('input_data', {})
    return {
        'mes': input_data.get('mes', cad.get('mes', 1)),
        'ano': input_data.get('ano', cad.get('ano', 2025)),
        'slots': input_data.get('slots', cad.get('slots', [])),
        'persona_id': input_data.get('persona_id', cad.get('persona_id', ed.get('persona_id', ''))),
    }


def gerar_calendario_mensal_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado do calendário."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': 'erro', 'raw': result}
    return _merge_outputs(state, 'gerar_calendario_mensal', result)


# ============================================================================
# 5. gerar_conteudo_redator
# ============================================================================
def gerar_conteudo_redator_input_func(state: dict) -> dict:
    """Extrai dados para geração de conteúdo."""
    input_data = state.get('input_data', {}) or state.get('previous_outputs', {}).get('P_content_start', {})
    return {
        'tipo_conteudo': input_data.get('tipo_conteudo', 'artigo'),
        'texto': input_data.get('texto', ''),
        'data_publicacao': input_data.get('data_publicacao', ''),
        'pilar_conteudo_id': input_data.get('pilar_conteudo_id', ''),
        'hashtags': input_data.get('hashtags', []),
    }


def gerar_conteudo_redator_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da geração de conteúdo."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': 'erro', 'raw': result}
    return _merge_outputs(state, 'gerar_conteudo_redator', result)


# ============================================================================
# 6. verificar_fatos_revisor
# ============================================================================
def verificar_fatos_revisor_input_func(state: dict) -> dict:
    """Extrai post_id e texto revisado para verificação de fatos."""
    prev = state.get('previous_outputs', {}).get('P_gerar_conteudo_done', {})
    input_data = state.get('input_data', {})
    return {
        'post_id': input_data.get('post_id', prev.get('post_id', '')),
        'texto_revisado': input_data.get('texto_revisado', prev.get('texto', '')),
    }


def verificar_fatos_revisor_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da verificação."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'verificar_fatos_revisor', result)


# ============================================================================
# 7. revisar_conteudo_usuario
# ============================================================================
def revisar_conteudo_usuario_input_func(state: dict) -> dict:
    """Extrai post_id e status para revisão de conteúdo."""
    prev = state.get('previous_outputs', {}).get('P_verificar_done', {})
    input_data = state.get('input_data', {})
    return {
        'post_id': input_data.get('post_id', prev.get('post_id', '')),
        'status': input_data.get('status', 'pendente'),
    }


def revisar_conteudo_usuario_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da revisão."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'revisar_conteudo_usuario', result)


# ============================================================================
# 8. agendar_publicacao_conteudo
# ============================================================================
def agendar_publicacao_conteudo_input_func(state: dict) -> dict:
    """Extrai post_id e data de agendamento."""
    prev = state.get('previous_outputs', {}).get('P_revisar_done', {})
    input_data = state.get('input_data', {})
    return {
        'post_id': input_data.get('post_id', prev.get('post_id', '')),
        'data_agendamento': input_data.get('data_agendamento', ''),
    }


def agendar_publicacao_conteudo_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado do agendamento."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'agendar_publicacao_conteudo', result)


# ============================================================================
# 9. publicar_conteudo_plataformas
# ============================================================================
def publicar_conteudo_plataformas_input_func(state: dict) -> dict:
    """Extrai post_id e status para publicação."""
    prev = state.get('previous_outputs', {}).get('P_agendar_done', {})
    input_data = state.get('input_data', {})
    return {
        'post_id': input_data.get('post_id', prev.get('post_id', '')),
        'status': input_data.get('status', 'publicado'),
    }


def publicar_conteudo_plataformas_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da publicação."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'publicar_conteudo_plataformas', result)


# ============================================================================
# 10. coletar_metricas_engajamento
# ============================================================================
def coletar_metricas_engajamento_input_func(state: dict) -> dict:
    """Extrai lista de post_ids para coleta de métricas."""
    input_data = state.get('input_data', {})
    # Pode receber lista_post_ids diretamente ou do output de publicar
    return {
        'lista_post_ids': input_data.get('lista_post_ids', []),
    }


def coletar_metricas_engajamento_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da coleta de métricas."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': 'erro', 'raw': result, 'lista_metricas': []}
    return _merge_outputs(state, 'coletar_metricas_engajamento', result)


# ============================================================================
# 11. classificar_comentarios_leads
# ============================================================================
def classificar_comentarios_leads_input_func(state: dict) -> dict:
    """Extrai lista de comentários para classificação."""
    input_data = state.get('input_data', {})
    return {
        'lista_comentario_ids': input_data.get('lista_comentario_ids', []),
        'categoria': input_data.get('categoria', ''),
    }


def classificar_comentarios_leads_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da classificação."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'classificar_comentarios_leads', result)


# ============================================================================
# 12. gerar_respostas_automaticas_comentarios
# ============================================================================
def gerar_respostas_automaticas_comentarios_input_func(state: dict) -> dict:
    """Extrai lista de comentários para gerar respostas."""
    input_data = state.get('input_data', {})
    return {
        'lista_comentario_ids': input_data.get('lista_comentario_ids', []),
    }


def gerar_respostas_automaticas_comentarios_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da geração de respostas."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'gerar_respostas_automaticas_comentarios', result)


# ============================================================================
# 13. identificar_leads_warm_inbound
# ============================================================================
def identificar_leads_warm_inbound_input_func(state: dict) -> dict:
    """Extrai lista de leads e prioridade."""
    input_data = state.get('input_data', {})
    return {
        'lista_lead_ids': input_data.get('lista_lead_ids', []),
        'prioridade': input_data.get('prioridade', 'alta'),
    }


def identificar_leads_warm_inbound_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da identificação de leads."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'identificar_leads_warm_inbound', result)


# ============================================================================
# 14. gerar_relatorios_semanais
# ============================================================================
def gerar_relatorios_semanais_input_func(state: dict) -> dict:
    """Extrai mês e ano para geração de relatório semanal."""
    input_data = state.get('input_data', {})
    return {
        'mes': input_data.get('mes', None),
        'ano': input_data.get('ano', None),
    }


def gerar_relatorios_semanais_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da geração de relatório."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'gerar_relatorios_semanais', result)


# ============================================================================
# 15. exportar_calendario_relatorios
# ============================================================================
def exportar_calendario_relatorios_input_func(state: dict) -> dict:
    """Extrai lista de IDs de calendários e formato de exportação."""
    input_data = state.get('input_data', {})
    prev_cal = state.get('previous_outputs', {}).get('P_gerar_calendario_done', {}).get('calendario_id', None)
    return {
        'lista_calendario_ids': input_data.get('lista_calendario_ids', [prev_cal] if prev_cal else []),
    }


def exportar_calendario_relatorios_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da exportação."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'exportar_calendario_relatorios', result)


# ============================================================================
# 16. sincronizar_agenda_google_calendar
# ============================================================================
def sincronizar_agenda_google_calendar_input_func(state: dict) -> dict:
    """Extrai lista de reuniões para sincronizar com Google Calendar."""
    input_data = state.get('input_data', {})
    return {
        'lista_reuniao_ids': input_data.get('lista_reuniao_ids', []),
    }


def sincronizar_agenda_google_calendar_output_func(state: dict, result: Any) -> dict:
    """Processa o resultado da sincronização."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            result = {'status': result}
    return _merge_outputs(state, 'sincronizar_agenda_google_calendar', result)


# ============================================================================
# Registro de tarefas para descoberta dinâmica pelo WebSocket Server
# ============================================================================
TASK_ADAPTERS: Dict[str, Dict[str, Any]] = {
    'cadastrar_persona_alvo': {
        'input_func': cadastrar_persona_alvo_input_func,
        'output_func': cadastrar_persona_alvo_output_func,
    },
    'editar_persona_alvo': {
        'input_func': editar_persona_alvo_input_func,
        'output_func': editar_persona_alvo_output_func,
    },
    'gerenciar_permissoes_usuario': {
        'input_func': gerenciar_permissoes_usuario_input_func,
        'output_func': gerenciar_permissoes_usuario_output_func,
    },
    'gerar_calendario_mensal': {
        'input_func': gerar_calendario_mensal_input_func,
        'output_func': gerar_calendario_mensal_output_func,
    },
    'gerar_conteudo_redator': {
        'input_func': gerar_conteudo_redator_input_func,
        'output_func': gerar_conteudo_redator_output_func,
    },
    'verificar_fatos_revisor': {
        'input_func': verificar_fatos_revisor_input_func,
        'output_func': verificar_fatos_revisor_output_func,
    },
    'revisar_conteudo_usuario': {
        'input_func': revisar_conteudo_usuario_input_func,
        'output_func': revisar_conteudo_usuario_output_func,
    },
    'agendar_publicacao_conteudo': {
        'input_func': agendar_publicacao_conteudo_input_func,
        'output_func': agendar_publicacao_conteudo_output_func,
    },
    'publicar_conteudo_plataformas': {
        'input_func': publicar_conteudo_plataformas_input_func,
        'output_func': publicar_conteudo_plataformas_output_func,
    },
    'coletar_metricas_engajamento': {
        'input_func': coletar_metricas_engajamento_input_func,
        'output_func': coletar_metricas_engajamento_output_func,
    },
    'classificar_comentarios_leads': {
        'input_func': classificar_comentarios_leads_input_func,
        'output_func': classificar_comentarios_leads_output_func,
    },
    'gerar_respostas_automaticas_comentarios': {
        'input_func': gerar_respostas_automaticas_comentarios_input_func,
        'output_func': gerar_respostas_automaticas_comentarios_output_func,
    },
    'identificar_leads_warm_inbound': {
        'input_func': identificar_leads_warm_inbound_input_func,
        'output_func': identificar_leads_warm_inbound_output_func,
    },
    'gerar_relatorios_semanais': {
        'input_func': gerar_relatorios_semanais_input_func,
        'output_func': gerar_relatorios_semanais_output_func,
    },
    'exportar_calendario_relatorios': {
        'input_func': exportar_calendario_relatorios_input_func,
        'output_func': exportar_calendario_relatorios_output_func,
    },
    'sincronizar_agenda_google_calendar': {
        'input_func': sincronizar_agenda_google_calendar_input_func,
        'output_func': sincronizar_agenda_google_calendar_output_func,
    },
}
