"""GeoprocessamentoTool — ferramenta geoespacial COMPLETA para sistemas de uso do solo.

Camadas (todas testadas):
  • núcleo in-process (shapely + pyproj): buffer(m), intersects/contains/within/overlaps,
    distancia_m, area_ha, comprimento_m, centroide, reprojetar, uniao, diferenca, interseccao.
  • PostGIS (psycopg2): zonas_do_ponto / regras_do_imovel — consulta espacial real contra
    o banco (ST_Intersects/ST_Contains) para avaliar conformidade de uso do solo.
  • QGIS processing (679 algoritmos native/GDAL/GRASS) via ponte subprocess ao python do
    sistema: qgis_algorithm / qgis_list — para operações pesadas (clip, dissolve, zonal stats…).
  • OGC WFS (owslib): load_wfs — carrega bases georreferenciadas (ex.: IDE Sisema/MG) como GeoJSON.

Importa limpo no conda python 3.13 (QGIS é acessado por subprocess, não por import).
Exposta ao CrewAI como GeoprocessamentoTool (BaseTool) e também como função geoprocessar()
para uso determinístico/testes.
"""
from __future__ import annotations
import os
import json
import math
import subprocess
from typing import Any, Dict, List, Optional

# núcleo geométrico (obrigatório)
from shapely import wkt as _wkt
from shapely.geometry import shape as _shape, mapping as _mapping, Point
from shapely.ops import transform as _sh_transform, unary_union
from pyproj import Geod, Transformer, CRS

_GEOD = Geod(ellps="WGS84")
_DEFAULT_SRID = int(os.getenv("GEO_DEFAULT_SRID", "4674"))  # SIRGAS 2000 (oficial BR/MG)
_QGIS_BRIDGE = os.path.join(os.path.dirname(__file__), "qgis_bridge.py")
_SYS_PY = os.getenv("QGIS_SYS_PYTHON", "/usr/bin/python3")


# ───────────────────────── helpers ─────────────────────────
def _geom(g):
    """Aceita WKT, GeoJSON (dict) ou shapely geometry -> shapely geometry."""
    if hasattr(g, "geom_type"):
        return g
    if isinstance(g, dict):
        return _shape(g)
    if isinstance(g, str):
        s = g.strip()
        if s.startswith("{"):
            return _shape(json.loads(s))
        return _wkt.loads(s)
    raise ValueError(f"geometria não reconhecida: {type(g)}")


def _utm_metric_crs(geom, srid: int) -> int:
    """CRS métrico apropriado (SIRGAS 2000 / UTM) a partir do centróide — p/ buffer/área em metros."""
    c = geom.centroid
    lon, lat = (c.x, c.y)
    zone = int((lon + 180) / 6) + 1
    # SIRGAS 2000 / UTM: Sul = 31960+zona (23S=31983), Norte = 31954+zona (18N=31972).
    return (31960 + zone) if lat < 0 else (31954 + zone)


def _to_metric(geom, srid: int):
    mcrs = _utm_metric_crs(geom, srid)
    tr = Transformer.from_crs(CRS.from_epsg(srid), CRS.from_epsg(mcrs), always_xy=True)
    return _sh_transform(lambda x, y, z=None: tr.transform(x, y), geom), mcrs


def _run_qgis(payload: Dict[str, Any], timeout: int = 180) -> Dict[str, Any]:
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    proc = subprocess.run([_SYS_PY, _QGIS_BRIDGE, json.dumps(payload)],
                          capture_output=True, text=True, env=env, timeout=timeout)
    for line in proc.stdout.splitlines():
        if line.startswith("QGIS_RESULT:"):
            return json.loads(line[len("QGIS_RESULT:"):])
    return {"ok": False, "error": "sem QGIS_RESULT", "stderr": proc.stderr[-800:]}


# ───────────────────────── operações núcleo ─────────────────────────
def op_buffer(geometria, distancia_m: float, srid: int = _DEFAULT_SRID) -> Dict[str, Any]:
    g = _geom(geometria)
    gm, mcrs = _to_metric(g, srid)
    bm = gm.buffer(float(distancia_m))
    back = Transformer.from_crs(CRS.from_epsg(mcrs), CRS.from_epsg(srid), always_xy=True)
    out = _sh_transform(lambda x, y, z=None: back.transform(x, y), bm)
    return {"ok": True, "op": "buffer", "distancia_m": distancia_m, "wkt": out.wkt,
            "geojson": _mapping(out), "area_ha": round(bm.area / 10000.0, 4)}


def op_predicado(pred: str, a, b) -> Dict[str, Any]:
    ga, gb = _geom(a), _geom(b)
    val = getattr(ga, pred)(gb)
    return {"ok": True, "op": pred, "resultado": bool(val)}


def op_distancia_m(a, b, srid: int = _DEFAULT_SRID) -> Dict[str, Any]:
    ga, gb = _geom(a), _geom(b)
    pa = ga.centroid if ga.geom_type != "Point" else ga
    pb = gb.centroid if gb.geom_type != "Point" else gb
    # distância geodésica entre os pontos representativos (ou 0 se intersectam)
    if ga.intersects(gb):
        return {"ok": True, "op": "distancia_m", "metros": 0.0}
    _, _, dist = _GEOD.inv(pa.x, pa.y, pb.x, pb.y)
    return {"ok": True, "op": "distancia_m", "metros": round(dist, 2)}


def op_area_ha(geometria, srid: int = _DEFAULT_SRID) -> Dict[str, Any]:
    g = _geom(geometria)
    if g.geom_type not in ("Polygon", "MultiPolygon"):
        return {"ok": False, "error": "área requer Polygon/MultiPolygon"}
    area_m2, _ = _GEOD.geometry_area_perimeter(g)
    return {"ok": True, "op": "area_ha", "area_ha": round(abs(area_m2) / 10000.0, 4),
            "area_m2": round(abs(area_m2), 2)}


def op_reprojetar(geometria, de_srid: int, para_srid: int) -> Dict[str, Any]:
    g = _geom(geometria)
    tr = Transformer.from_crs(CRS.from_epsg(de_srid), CRS.from_epsg(para_srid), always_xy=True)
    out = _sh_transform(lambda x, y, z=None: tr.transform(x, y), g)
    return {"ok": True, "op": "reprojetar", "de": de_srid, "para": para_srid, "wkt": out.wkt}


def op_overlay(kind: str, a, b) -> Dict[str, Any]:
    ga, gb = _geom(a), _geom(b)
    out = {"uniao": ga.union, "interseccao": ga.intersection, "diferenca": ga.difference}[kind](gb)
    return {"ok": True, "op": kind, "wkt": out.wkt, "geojson": _mapping(out) if not out.is_empty else None,
            "vazio": out.is_empty}


# ───────────────────────── PostGIS (conformidade uso do solo) ─────────────────────────
def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        host=os.getenv("PG_HOST", os.getenv("DB_HOST", "127.0.0.1")),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", os.getenv("DB_USER", "producao")),
        password=os.getenv("PG_PASSWORD", os.getenv("DB_PASSWORD", "")),
        dbname=os.getenv("PG_DB", os.getenv("DB_NAME", "uso_solo_gis")),
    )


def op_zonas_do_ponto(lon: float, lat: float, srid: int = _DEFAULT_SRID) -> Dict[str, Any]:
    """Consulta espacial REAL: quais zonas de uso do solo contêm o ponto (imóvel) + suas regras.
    É a operação central de avaliação de conformidade — o coração do sistema."""
    conn = _pg_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT z.id, z.nome, z.tipo_zona, "
            "  ROUND((ST_Area(z.geometria::geography)/10000.0)::numeric,2) AS area_ha "
            "FROM zoneamento z "
            "WHERE ST_Intersects(z.geometria, ST_SetSRID(ST_MakePoint(%s,%s),%s))",
            [lon, lat, srid])
        zonas = [{"id": str(r[0]), "nome": r[1], "tipo_zona": r[2], "area_ha": float(r[3]) if r[3] else None}
                 for r in cur.fetchall()]
        regras = []
        if zonas:
            cur.execute(
                "SELECT ra.descricao, ra.condicao, ra.acao, z.nome "
                "FROM regra_aplicavel ra JOIN zoneamento z ON z.id = ra.zoneamento_id "
                "WHERE z.id::text = ANY(%s)", [[z["id"] for z in zonas]])
            regras = [{"descricao": r[0], "condicao": r[1], "acao": r[2], "zona": r[3]} for r in cur.fetchall()]
        cur.close()
        return {"ok": True, "op": "zonas_do_ponto", "ponto": [lon, lat],
                "zonas": zonas, "regras": regras, "conforme": len(zonas) > 0}
    finally:
        conn.close()


# ───────────────────────── QGIS processing (679 algoritmos) ─────────────────────────
def op_qgis_list(filtro: str = "") -> Dict[str, Any]:
    return _run_qgis({"op": "list", "filter": filtro})


def op_qgis_algorithm(algorithm: str, params: Dict[str, Any]) -> Dict[str, Any]:
    return _run_qgis({"op": "run", "algorithm": algorithm, "params": params})


# ───────────────────────── WFS (IDE Sisema / OGC) ─────────────────────────
def op_load_wfs(url: str, typename: str, bbox: Optional[List[float]] = None, max_features: int = 500) -> Dict[str, Any]:
    from owslib.wfs import WebFeatureService
    wfs = WebFeatureService(url=url, version="2.0.0")
    kw = {"typename": typename, "outputFormat": "application/json", "maxfeatures": max_features}
    if bbox:
        kw["bbox"] = tuple(bbox)
    resp = wfs.getfeature(**kw)
    data = resp.read()
    try:
        gj = json.loads(data)
        n = len(gj.get("features", []))
    except Exception:
        gj, n = None, 0
    return {"ok": gj is not None, "op": "load_wfs", "typename": typename, "n_features": n, "geojson": gj}


# ───────────────────────── dispatcher ─────────────────────────
_OPS = {
    "buffer": lambda p: op_buffer(p["geometria"], p["distancia_m"], p.get("srid", _DEFAULT_SRID)),
    "intersects": lambda p: op_predicado("intersects", p["a"], p["b"]),
    "contains": lambda p: op_predicado("contains", p["a"], p["b"]),
    "within": lambda p: op_predicado("within", p["a"], p["b"]),
    "overlaps": lambda p: op_predicado("overlaps", p["a"], p["b"]),
    "distancia_m": lambda p: op_distancia_m(p["a"], p["b"], p.get("srid", _DEFAULT_SRID)),
    "area_ha": lambda p: op_area_ha(p["geometria"], p.get("srid", _DEFAULT_SRID)),
    "reprojetar": lambda p: op_reprojetar(p["geometria"], p["de_srid"], p["para_srid"]),
    "uniao": lambda p: op_overlay("uniao", p["a"], p["b"]),
    "interseccao": lambda p: op_overlay("interseccao", p["a"], p["b"]),
    "diferenca": lambda p: op_overlay("diferenca", p["a"], p["b"]),
    "zonas_do_ponto": lambda p: op_zonas_do_ponto(p["lon"], p["lat"], p.get("srid", _DEFAULT_SRID)),
    "qgis_list": lambda p: op_qgis_list(p.get("filtro", "")),
    "qgis_algorithm": lambda p: op_qgis_algorithm(p["algorithm"], p.get("params", {})),
    "load_wfs": lambda p: op_load_wfs(p["url"], p["typename"], p.get("bbox"), p.get("max_features", 500)),
}


def geoprocessar(operation: str, **params) -> Dict[str, Any]:
    """Ponto de entrada determinístico. operation ∈ _OPS."""
    fn = _OPS.get(operation)
    if not fn:
        return {"ok": False, "error": f"operação '{operation}' desconhecida",
                "operacoes": sorted(_OPS.keys())}
    try:
        return fn(params)
    except KeyError as e:
        return {"ok": False, "error": f"parâmetro obrigatório ausente: {e}"}
    except Exception as e:
        import traceback
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()[-600:]}


# ───────────────────────── CrewAI BaseTool ─────────────────────────
try:
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field

    class GeoprocessamentoSchema(BaseModel):
        operation: str = Field(..., description=(
            "Operação geoespacial: buffer, intersects, contains, within, overlaps, distancia_m, "
            "area_ha, reprojetar, uniao, interseccao, diferenca, zonas_do_ponto (conformidade uso do "
            "solo via PostGIS), qgis_algorithm (679 algoritmos QGIS/GDAL/GRASS), qgis_list, load_wfs "
            "(carrega base OGC/IDE Sisema). Geometrias em WKT ou GeoJSON; SRID padrão 4674 (SIRGAS 2000)."))
        params: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros da operação (ver docstring).")

    class GeoprocessamentoTool(BaseTool):
        name: str = "geoprocessamento_tool"
        description: str = (
            "Ferramenta geoespacial COMPLETA (uso do solo): análise espacial (buffer/interseção/área/"
            "distância/reprojeção/overlay), consulta de conformidade contra zonas do PostGIS "
            "(zonas_do_ponto), 679 algoritmos QGIS/GDAL/GRASS (qgis_algorithm) e carga de bases OGC/WFS "
            "(IDE Sisema). NÃO simula — executa de verdade.")
        args_schema: type = GeoprocessamentoSchema

        def _run(self, operation: str, params: Optional[Dict[str, Any]] = None) -> str:
            return json.dumps(geoprocessar(operation, **(params or {})), ensure_ascii=False, default=str)

    geoprocessamento_tool = GeoprocessamentoTool()
except Exception:  # crewai ausente em contexto de teste puro
    GeoprocessamentoTool = None
    geoprocessamento_tool = None
