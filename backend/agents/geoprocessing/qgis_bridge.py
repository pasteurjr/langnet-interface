#!/usr/bin/env python3
"""Ponte QGIS headless — roda no PYTHON DO SISTEMA (3.12, para o qual o binding
python3-qgis foi compilado). NÃO importa no conda python 3.13. É invocado por
subprocess pela GeoprocessamentoTool.

Uso:
  QT_QPA_PLATFORM=offscreen python3 qgis_bridge.py '<json>'
onde <json> = {"op": "run", "algorithm": "native:buffer", "params": {...}}
           ou {"op": "list", "filter": "buffer"}

Entrada/saída em JSON pelo stdout (linha começando com QGIS_RESULT:).
Suporta GeoJSON inline como input/output das camadas vetoriais (sem arquivos temporários
quando possível): params com valor {"geojson": {...}} viram uma layer em memória; saídas
'OUTPUT' são devolvidas como GeoJSON.
"""
import sys, json, os, tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _init():
    from qgis.core import QgsApplication
    qgs = QgsApplication([], False)
    qgs.initQgis()
    sys.path.append("/usr/share/qgis/python/plugins")
    import processing  # noqa
    from processing.core.Processing import Processing
    Processing.initialize()
    return qgs


def _geojson_to_layer(gj, name="mem"):
    """Escreve o GeoJSON num arquivo temporário e devolve o caminho (input p/ o algoritmo)."""
    fd, path = tempfile.mkstemp(suffix=".geojson", prefix="qgis_in_")
    with os.fdopen(fd, "w") as f:
        json.dump(gj, f)
    return path


def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else json.loads(sys.stdin.read())
    op = payload.get("op", "run")
    qgs = _init()
    try:
        import processing
        from qgis.core import QgsApplication

        if op == "list":
            filt = (payload.get("filter") or "").lower()
            algs = QgsApplication.processingRegistry().algorithms()
            items = [{"id": a.id(), "name": a.displayName(), "provider": a.provider().name()}
                     for a in algs if not filt or filt in a.id().lower() or filt in a.displayName().lower()]
            print("QGIS_RESULT:" + json.dumps({"ok": True, "count": len(items), "algorithms": items[:200]}))
            return

        # op == run
        alg = payload["algorithm"]
        params = dict(payload.get("params") or {})
        tmp_inputs = []
        # inputs GeoJSON inline -> arquivo temporário
        for k, v in list(params.items()):
            if isinstance(v, dict) and "geojson" in v:
                p = _geojson_to_layer(v["geojson"])
                tmp_inputs.append(p)
                params[k] = p
        # saída padrão em memória (GeoJSON) quando não especificada
        wants_output = "OUTPUT" not in params
        out_path = None
        if wants_output:
            fd, out_path = tempfile.mkstemp(suffix=".geojson", prefix="qgis_out_")
            os.close(fd)
            params["OUTPUT"] = out_path

        res = processing.run(alg, params)

        result = {"ok": True, "algorithm": alg, "raw": {}}
        for k, v in res.items():
            result["raw"][k] = str(v)
        # devolve o OUTPUT como GeoJSON se for camada em arquivo
        if out_path and os.path.exists(out_path):
            with open(out_path) as f:
                try:
                    result["output_geojson"] = json.load(f)
                except Exception:
                    result["output_geojson"] = None
        print("QGIS_RESULT:" + json.dumps(result, default=str))

        for p in tmp_inputs + ([out_path] if out_path else []):
            try:
                os.remove(p)
            except Exception:
                pass
    except Exception as e:
        import traceback
        print("QGIS_RESULT:" + json.dumps({"ok": False, "error": str(e),
                                           "traceback": traceback.format_exc()}))
    finally:
        qgs.exitQgis()


if __name__ == "__main__":
    main()
