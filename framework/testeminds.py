from mindsdb_sdk import connect

NEW_KEY = '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'

srv = connect('http://camerascasas.no-ip.info:47334')
proj = srv.projects.get('mindsdb')

# 1 agente
ag = proj.agents.get('natural_language_database_searcher')
p = ag.params or {}; m = (p.get('model') or {})
m['api_key'] = NEW_KEY                      # <- em AGENTS é "api_key"
p['model'] = m; ag.params = p
proj.agents.update(ag.name, ag)

# em lote (todos do projeto que usam openai)
for ag in proj.agents.list():
    p = ag.params or {}; m = (p.get('model') or {})
    if (m.get('provider') or '').lower() == 'openai':
        m['api_key'] = NEW_KEY
        p['model'] = m; ag.params = p
        proj.agents.update(ag.name, ag)
