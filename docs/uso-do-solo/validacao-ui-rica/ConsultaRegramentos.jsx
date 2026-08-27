import React, { useEffect, useRef, useState } from "react";
import { runTask } from "./wsClient";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";

// Traceability: UC UC-001 | FR   (tela rica auto-gerada por LangNet)
export default function ConsultaRegramentos() {
  const mapRef = useRef(null);
  const [wkt, setWkt] = useState("");
  const [form, setForm] = useState({});
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [file, setFile] = useState(null);

  useEffect(() => {
    if (!true || !mapRef.current || mapRef.current._built) return;
    mapRef.current._built = true;
    const map = L.map(mapRef.current).setView([-19.9, -44.0], 12);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "\u00a9 OpenStreetMap" }).addTo(map);
    const drawn = new L.FeatureGroup(); map.addLayer(drawn);
    const dc = new L.Control.Draw({ edit: { featureGroup: drawn },
      draw: { polygon: true, rectangle: true, marker: true, polyline: false, circle: false, circlemarker: false } });
    map.addControl(dc);
    map.on(L.Draw.Event.CREATED, (e) => {
      drawn.clearLayers(); drawn.addLayer(e.layer);
      const g = e.layer.toGeoJSON().geometry; setWkt(toWKT(g));
    });
  }, []);

  function toWKT(g) {
    const p = (c) => c[0] + " " + c[1];
    if (g.type === "Point") return "POINT(" + p(g.coordinates) + ")";
    if (g.type === "Polygon") return "POLYGON((" + g.coordinates[0].map(p).join(", ") + "))";
    return "";
  }

  async function submit() {
    setBusy(true); setErr(""); setResult(null);
    try {
      const input = { ...form };
      if (true && wkt) input["localizacao_geografica"] = wkt;
      const r = await runTask("consultar_regramentos_ambientais", input);
      setResult(r);
    } catch (e) { setErr(String((e && e.message) || e)); }
    setBusy(false);
  }

  const chartData = (result && (result.items || result.dados || result.data)) || [];

  return (
    <div data-uc="UC-001" data-fr="" style={{ padding: 24, maxWidth: 1100 }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, color: "#0f172a", marginBottom: 16 }}>Consulta de Regramentos</h1>
      <div style={{marginBottom:10}}><label style={{display:"block",fontSize:13,fontWeight:600,color:"#334155",marginBottom:4}}>Nome do Empreendimento</label><input value={form["nome"]||""} onChange={(e)=>setForm({...form,["nome"]:e.target.value})} style={{width:"100%",padding:"9px 12px",border:"1px solid #cbd5e1",borderRadius:8,fontSize:14}} /></div><div style={{marginBottom:10}}><label style={{display:"block",fontSize:13,fontWeight:600,color:"#334155",marginBottom:4}}>Porte</label><input value={form["porte"]||""} onChange={(e)=>setForm({...form,["porte"]:e.target.value})} style={{width:"100%",padding:"9px 12px",border:"1px solid #cbd5e1",borderRadius:8,fontSize:14}} /></div><div style={{marginBottom:10}}><label style={{display:"block",fontSize:13,fontWeight:600,color:"#334155",marginBottom:4}}>Potencial Poluidor</label><input value={form["potencial_poluidor"]||""} onChange={(e)=>setForm({...form,["potencial_poluidor"]:e.target.value})} style={{width:"100%",padding:"9px 12px",border:"1px solid #cbd5e1",borderRadius:8,fontSize:14}} /></div><div style={{marginBottom:10}}><label style={{display:"block",fontSize:13,fontWeight:600,color:"#334155",marginBottom:4}}>Município</label><input value={form["municipio_id"]||""} onChange={(e)=>setForm({...form,["municipio_id"]:e.target.value})} style={{width:"100%",padding:"9px 12px",border:"1px solid #cbd5e1",borderRadius:8,fontSize:14}} /></div>
      <div style={{display:"flex",gap:16,marginTop:8}}><div style={{flex:2}}><div style={{fontSize:12,color:"#64748b",marginBottom:6}}>Desenhe a área do empreendimento no mapa:</div><div ref={mapRef} style={{height:420,borderRadius:12,border:"1px solid #cbd5e1"}} />{wkt && <div style={{fontSize:11,color:"#16a34a",marginTop:6}}>Geometria capturada ✓</div>}</div><div style={{flex:1}}><div style={{fontSize:12,fontWeight:600,color:"#334155",marginBottom:6}}>Resultado da análise</div><div style={{background:"#f8fafc",border:"1px solid #e2e8f0",borderRadius:10,padding:14,minHeight:120,fontSize:13}}>{result ? <pre style={{whiteSpace:"pre-wrap",margin:0}}>{JSON.stringify(result,null,2)}</pre> : <span style={{color:"#94a3b8"}}>Desenhe a área e clique em Nova Consulta.</span>}</div></div></div>
      
      <button onClick={submit} disabled={busy}
        style={{ marginTop: 16, background: busy ? "#94a3b8" : "#4f46e5", color: "#fff", padding: "10px 18px", borderRadius: 8, border: 0, fontWeight: 600, cursor: "pointer" }}>
        {busy ? "Processando..." : "Nova Consulta"}
      </button>
      {err && <div style={{ color: "#b91c1c", marginTop: 10 }}>{err}</div>}
      
      {result && !true && <pre style={{ marginTop: 14, background: "#f6f8fa", padding: 14, borderRadius: 8, fontSize: 12, overflow: "auto" }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
