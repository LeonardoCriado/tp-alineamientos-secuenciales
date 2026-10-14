#!/usr/bin/env python3
"""
Desafío VII: búsqueda BLAST remota en NCBI (no usa BLAST local).
Secuencia de entrada: secuencia.fasta
Parámetros pedidos: PROGRAM=blastp, DATABASE=nr, EXPECT=100, HITLIST_SIZE=20000.

Uso:
    python3 blast_vii_remote.py [--fasta secuencia.fasta] [--email TU_EMAIL] [--rid RID_EXISTENTE]

El script realiza estos pasos:
  1. PUT a https://blast.ncbi.nlm.nih.gov/Blast.cgi (CMD=Put) y obtiene RID/RTOE.
  2. Polling con CMD=Get + FORMAT_OBJECT=SearchInfo hasta Status=READY.
  3. Descarga las tablas (CSV y Text con ALIGNMENT_VIEW=Tabular) y un JSON2_S de respaldo.
  4. Guarda la tabla en resultados/blast_vii.tsv
     con identificador, descripción, identidad, cobertura, E-value y score.
     Si la API no devuelve algún dato, el script lo informa y no inventa valores.
  5. Genera resultados/blast_vii_filtrado_e100_cov70.tsv con E-value<=100 y cobertura>=70%.

Pautas de NCBI consideradas (https://blast.ncbi.nlm.nih.gov/doc/blast-help/developerinfo.html):
  - Esperar al menos 10 s entre solicitudes al servidor.
  - Consultar cada RID como máximo una vez por minuto durante el polling.
  - Enviar TOOL y EMAIL como datos de contacto.
  - Usar el servicio para una búsqueda, no de forma masiva.

Corrida iniciada el 2026-10-12/13:
  RID=CUZ2AG6F016, RTOE=25965, QUERY_LEN=133, estado inicial=WAITING/Searching.
  El RID se guarda en resultados/RID.txt. Los registros de ejecución se generan
  si se vuelve a correr el script.
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FASTA_DEFAULT = BASE_DIR / "secuencia.fasta"
OUT_DIR = BASE_DIR / "resultados"
BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
TOOL = "BioinfoTP_AlineamientosSecuenciales"

# Parámetros del desafío VII
PROGRAM = "blastp"
DATABASE = "nr"
EXPECT = "100"
HITLIST_SIZE = "20000"

QUERY_LEN = 133  # Se vuelve a calcular desde el FASTA; este es el largo esperado.


def log(msg: str):
    print(msg, flush=True)


def read_query(fasta: Path) -> str:
    seq = "".join(
        line.strip() for line in fasta.read_text().splitlines() if not line.startswith(">")
    )
    return seq


def http_post(params: dict) -> str:
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(BLAST_URL, data=data)
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", errors="replace")


def http_get(params: dict) -> str:
    url = BLAST_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_rid_rtoe(text: str):
    rid = re.search(r"RID\s*=\s*([A-Z0-9]+)", text)
    rtoe = re.search(r"RTOE\s*=\s*([0-9]+)", text)
    return (rid.group(1) if rid else None, int(rtoe.group(1)) if rtoe else None)


def submit(query: str, email: str) -> tuple[str, int | None]:
    params = {
        "CMD": "Put",
        "PROGRAM": PROGRAM,
        "DATABASE": DATABASE,
        "QUERY": query,
        "EXPECT": EXPECT,
        "HITLIST_SIZE": HITLIST_SIZE,
        "TOOL": TOOL,
        "EMAIL": email,
    }
    log(f"[PUT] PROGRAM={PROGRAM} DATABASE={DATABASE} EXPECT={EXPECT} "
        f"HITLIST_SIZE={HITLIST_SIZE} TOOL={TOOL} EMAIL={email}")
    resp = http_post(params)
    rid, rtoe = parse_rid_rtoe(resp)
    if not rid:
        (OUT_DIR / "put_response.html").write_text(resp)
        raise RuntimeError("No se obtuvo RID. Respuesta guardada en resultados/put_response.html")
    log(f"[PUT] RID={rid} RTOE={rtoe}")
    return rid, rtoe


def poll_until_ready(rid: str, email: str, max_tries: int = 180) -> None:
    for i in range(1, max_tries + 1):
        # NCBI recomienda consultar un mismo RID como máximo una vez por minuto.
        time.sleep(60)
        info = http_get({"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo", "TOOL": TOOL})
        m = re.search(r"Status\s*=\s*(\w+)", info)
        status = m.group(1) if m else "SIN_STATUS_HTML"
        # En la respuesta HTML, el estado aparece en un bloque QBlastInfo.
        log(f"[POLL {i}] Status={status} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
        if "Status=READY" in info:
            # Si el estado es READY, se puede continuar con la descarga.
            return
        if "Status=FAILED" in info:
            raise RuntimeError("BLAST devolvió Status=FAILED")
        if "Status=UNKNOWN" in info:
            raise RuntimeError("BLAST devolvió Status=UNKNOWN (RID expirado/inválido)")
    raise TimeoutError("Polling agotado sin READY")


def download_results(rid: str) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = {}
    # 1) CSV tabular, que después se convierte a TSV.
    log("[GET] descargando tabla CSV...")
    csv_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "CSV",
        "ALIGNMENT_VIEW": "Tabular", "DESCRIPTIONS": HITLIST_SIZE,
        "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["csv"] = OUT_DIR / "blast_vii.csv_raw.csv"
    files["csv"].write_text(csv_text)
    log(f"  -> {files['csv']} ({len(csv_text)} bytes)")
    time.sleep(11)  # Espera más de 10 segundos antes de la siguiente solicitud.

    # 2) Tabla en formato Text.
    log("[GET] descargando tabla en formato Text...")
    tab_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "Text",
        "ALIGNMENT_VIEW": "Tabular", "DESCRIPTIONS": HITLIST_SIZE,
        "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["tab"] = OUT_DIR / "blast_vii.tabular.txt"
    files["tab"].write_text(tab_text)
    log(f"  -> {files['tab']} ({len(tab_text)} bytes)")
    time.sleep(11)  # Espera más de 10 segundos antes de la siguiente solicitud.

    # 3) JSON2_S como respaldo para recuperar las descripciones.
    log("[GET] descargando JSON2_S...")
    js_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "JSON2_S",
        "DESCRIPTIONS": HITLIST_SIZE, "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["json"] = OUT_DIR / "blast_vii.json"
    files["json"].write_text(js_text)
    log(f"  -> {files['json']} ({len(js_text)} bytes)")
    time.sleep(11)  # Espera más de 10 segundos antes de la siguiente solicitud.

    # 4) Resultado Text completo para inspección.
    log("[GET] descargando resultado completo en formato Text...")
    txt = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "Text",
        "DESCRIPTIONS": HITLIST_SIZE, "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["txt"] = OUT_DIR / "blast_vii.texto.txt"
    files["txt"].write_text(txt)
    log(f"  -> {files['txt']} ({len(txt)} bytes)")
    return files


def build_tsv(files: dict, query_len: int) -> Path:
    """Construye la tabla de resultados sin aplicar filtros.

    El tabular NCBI (outfmt6-like) NO trae 'descripción' ni 'cobertura' directa:
      columnas típicas: qacc sacc pident length mismatch gapopen qstart qend sstart send evalue bitscore
    Por eso: cobertura = (qend-qstart+1)/query_len*100 y descripción se une desde JSON2_S.
    Si la API trunca cantidad/formato, se documenta y NO se simulan hits.
    """
    csv_path = files["csv"]
    json_path = files["json"]
    lines = csv_path.read_text().splitlines()
    # El CSV tabular de NCBI puede traer comentarios '#' o no incluir encabezado.
    rows = [l for l in lines if l.strip() and not l.startswith("#")]
    header = None
    if rows and any(k in rows[0].lower() for k in ["query", "subject", "evalue", "pident", "%"]):
        header = [h.strip() for h in rows[0].split(",")]
        rows = rows[1:]
    log(f"[TSV] filas tabulares crudas (sin header): {len(rows)} (pedidas: {HITLIST_SIZE})")
    if header:
        log(f"[TSV] header tabular: {header}")

    # Mapa de accesiones a descripciones, tomado de JSON2_S.
    descr = {}
    try:
        js = json.loads(json_path.read_text())
        # En JSON2_S, la lista de hits está dentro de report/results/search.
        results = js.get("BlastOutput2", {}).get("report", {}).get("results", {}).get("search", {}).get("hits", [])
        for h in results:
            acc = h.get("acc") or h.get("accession") or str(h.get("num", ""))
            title = h.get("descr", {}).get("title", "") if isinstance(h.get("descr"), dict) else h.get("title", "")
            if not title:
                title = h.get("descr", "") if isinstance(h.get("descr"), str) else ""
            descr[str(acc)] = title
            for ids in h.get("hsps", []):
                pass
        log(f"[TSV] descripciones extraídas de JSON: {len(descr)}")
    except Exception as e:
        log(f"[TSV] AVISO: no se pudieron leer las descripciones del JSON: {e}")

    out = OUT_DIR / "blast_vii.tsv"
    cols = ["sacc", "descripcion", "pident", "cobertura_query_pct",
            "evalue", "bitscore", "qstart", "qend", "sstart", "send",
            "alen", "mismatch", "gapopen"]
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        n = 0
        for r in rows:
            p = [c.strip() for c in r.split(",")]
            # outfmt6 suele tener 12 columnas. Si el formato cambia, se omiten filas incompletas.
            if len(p) < 12:
                continue
            qacc, sacc, pident, length, mismatch, gapopen, qstart, qend, sstart, send, evalue, bitscore = p[:12]
            try:
                cov = (int(qend) - int(qstart) + 1) / query_len * 100 if query_len else 0.0
            except ValueError:
                cov = 0.0
            w.writerow({
                "sacc": sacc,
                "descripcion": descr.get(sacc, ""),
                "pident": pident,
                "cobertura_query_pct": f"{cov:.2f}",
                "evalue": evalue,
                "bitscore": bitscore,
                "qstart": qstart, "qend": qend, "sstart": sstart, "send": send,
                "alen": length, "mismatch": mismatch, "gapopen": gapopen,
            })
            n += 1
    log(f"[TSV] Se guardaron {n} hits sin filtrar en {out}.")
    if n < int(HITLIST_SIZE):
        log(f"[TSV] NOTA: se pidieron {HITLIST_SIZE} hits y la API devolvió {n}. "
            "La respuesta puede estar limitada por DESCRIPTIONS/ALIGNMENTS o por el servidor. "
            "No se agregan hits faltantes.")
    return out


def filtrar_e100_cov70(tsv_in: Path) -> Path:
    out = OUT_DIR / "blast_vii_filtrado_e100_cov70.tsv"
    kept, total = 0, 0
    with tsv_in.open() as fin, out.open("w", newline="") as fout:
        r = csv.DictReader(fin, delimiter="\t")
        w = csv.DictWriter(fout, fieldnames=r.fieldnames, delimiter="\t")
        w.writeheader()
        for row in r:
            total += 1
            try:
                ev = float(row["evalue"])
                cov = float(row["cobertura_query_pct"])
            except ValueError:
                continue
            if ev <= 100 and cov >= 70:
                w.writerow(row)
                kept += 1
    log(f"[FILTRO] E-value<=100 y cobertura>=70%: {kept} de {total} hits -> {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", default=str(FASTA_DEFAULT))
    ap.add_argument("--email", default="student@example.org",
                    help="Email de contacto, según la pauta de NCBI. Reemplazá el valor de ejemplo.")
    ap.add_argument("--rid", default=None, help="Reanudar una búsqueda existente con su RID.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    query = read_query(Path(args.fasta))
    global QUERY_LEN
    QUERY_LEN = len(query)
    log(f"Query len={QUERY_LEN} desde {args.fasta}")

    if args.rid:
        rid = args.rid
        log(f"Reanudando RID existente: {rid}")
    else:
        rid, rtoe = submit(query, args.email)
        (OUT_DIR / "RID.txt").write_text(rid + "\n")
        log(f"Si se interrumpe el script, podés reanudar con: python3 {Path(__file__).name} --rid {rid}")
        # RTOE es un tiempo estimado; durante el polling se esperan 60 s entre consultas.
        if rtoe and rtoe > 60:
            log(f"NCBI estima {rtoe} s de espera (RTOE); se consultará el estado cada 60 s.")

    poll_until_ready(rid, args.email)
    files = download_results(rid)
    tsv = build_tsv(files, QUERY_LEN)
    filtrar_e100_cov70(tsv)
    log("Listo. Revisá resultados/blast_vii.tsv y resultados/blast_vii_filtrado_e100_cov70.tsv")


if __name__ == "__main__":
    sys.exit(main())
