#!/usr/bin/env python3
"""
Desafío VII — BLAST remoto (NCBI URLAPI, sin BLAST local).
Secuencia: secuencia.fasta
Parámetros exigidos: PROGRAM=blastp, DATABASE=nr, EXPECT=100, HITLIST_SIZE=20000.

Uso:
    python3 blast_vii_remote.py [--fasta secuencia.fasta] [--email TU_EMAIL] [--rid RID_EXISTENTE]

Qué hace:
  1. PUT a https://blast.ncbi.nlm.nih.gov/Blast.cgi (CMD=Put) y obtiene RID/RTOE.
  2. Polling con CMD=Get + FORMAT_OBJECT=SearchInfo hasta Status=READY.
  3. Descarga tabular (CSV y Text con ALIGNMENT_VIEW=Tabular) + JSON2_S de respaldo.
  4. Guarda el resultado original sin modificar en resultados/blast_vii.tsv
     (con identificador, descripción, % identidad, cobertura, E-value y score;
      si la API no lo permite, lo explica sin simular datos).
  5. Genera resultados/blast_vii_filtrado_e100_cov70.tsv con E-value<=100 y cobertura>=70%.

Pautas NCBI respetadas (https://blast.ncbi.nlm.nih.gov/doc/blast-help/developerinfo.html):
  - No contactar al servidor más de 1 vez cada 10 s  -> sleep(10+) entre requests.
  - No consultar el mismo RID más de 1 vez por minuto -> sleep(60) en polling.
  - Enviar TOOL y EMAIL para contacto.
  - Una sola búsqueda (no uso masivo).

Evidencia de la corrida del 2026-10-12/13:
  RID=CUZ2AG6F016, RTOE=25965, QUERY_LEN=133, Status inicial=WAITING/Searching.
  Ver resultados/RID.txt y resultados/*.log si se re-ejecuta.
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

QUERY_LEN = 133  # se recalcula desde el fasta; valor esperado para secuencia_problema


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
        # Pauta NCBI: mismo RID no más de 1 vez/min
        time.sleep(60)
        info = http_get({"CMD": "Get", "RID": rid, "FORMAT_OBJECT": "SearchInfo", "TOOL": TOOL})
        m = re.search(r"Status\s*=\s*(\w+)", info)
        status = m.group(1) if m else "SIN_STATUS_HTML"
        # En HTML el bloque es <!--QBlastInfoBegin Status=WAITING ...-->
        log(f"[POLL {i}] Status={status} {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
        if "Status=READY" in info:
            # Verificación extra: intentar HTML de estado
            return
        if "Status=FAILED" in info:
            raise RuntimeError("BLAST devolvió Status=FAILED")
        if "Status=UNKNOWN" in info:
            raise RuntimeError("BLAST devolvió Status=UNKNOWN (RID expirado/inválido)")
    raise TimeoutError("Polling agotado sin READY")


def download_results(rid: str) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = {}
    # 1) CSV tabular (ideal para TSV)
    log("[GET] descargando CSV tabular ...")
    csv_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "CSV",
        "ALIGNMENT_VIEW": "Tabular", "DESCRIPTIONS": HITLIST_SIZE,
        "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["csv"] = OUT_DIR / "blast_vii.csv_raw.csv"
    files["csv"].write_text(csv_text)
    log(f"  -> {files['csv']} ({len(csv_text)} bytes)")
    time.sleep(11)  # pauta: 1 req / 10 s

    # 2) Text tabular
    log("[GET] descargando Text tabular ...")
    tab_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "Text",
        "ALIGNMENT_VIEW": "Tabular", "DESCRIPTIONS": HITLIST_SIZE,
        "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["tab"] = OUT_DIR / "blast_vii.tabular.txt"
    files["tab"].write_text(tab_text)
    log(f"  -> {files['tab']} ({len(tab_text)} bytes)")
    time.sleep(11)

    # 3) JSON2_S (trae descripción + HSPs completos, respaldo para unir títulos)
    log("[GET] descargando JSON2_S ...")
    js_text = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "JSON2_S",
        "DESCRIPTIONS": HITLIST_SIZE, "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["json"] = OUT_DIR / "blast_vii.json"
    files["json"].write_text(js_text)
    log(f"  -> {files['json']} ({len(js_text)} bytes)")
    time.sleep(11)

    # 4) Text completo (inspección humana)
    log("[GET] descargando Text completo ...")
    txt = http_get({
        "CMD": "Get", "RID": rid, "FORMAT_TYPE": "Text",
        "DESCRIPTIONS": HITLIST_SIZE, "ALIGNMENTS": HITLIST_SIZE, "TOOL": TOOL,
    })
    files["txt"] = OUT_DIR / "blast_vii.texto.txt"
    files["txt"].write_text(txt)
    log(f"  -> {files['txt']} ({len(txt)} bytes)")
    return files


def build_tsv(files: dict, query_len: int) -> Path:
    """Construye resultados/blast_vii.tsv original (sin filtrar).

    El tabular NCBI (outfmt6-like) NO trae 'descripción' ni 'cobertura' directa:
      columnas típicas: qacc sacc pident length mismatch gapopen qstart qend sstart send evalue bitscore
    Por eso: cobertura = (qend-qstart+1)/query_len*100 y descripción se une desde JSON2_S.
    Si la API trunca cantidad/formato, se documenta y NO se simulan hits.
    """
    csv_path = files["csv"]
    json_path = files["json"]
    lines = csv_path.read_text().splitlines()
    # El CSV tabular de NCBI puede venir con líneas comentario '#' o sin header.
    rows = [l for l in lines if l.strip() and not l.startswith("#")]
    header = None
    if rows and any(k in rows[0].lower() for k in ["query", "subject", "evalue", "pident", "%"]):
        header = [h.strip() for h in rows[0].split(",")]
        rows = rows[1:]
    log(f"[TSV] filas tabulares crudas (sin header): {len(rows)} (pedidas: {HITLIST_SIZE})")
    if header:
        log(f"[TSV] header tabular: {header}")

    # Mapa sacc -> descripción desde JSON2_S
    descr = {}
    try:
        js = json.loads(json_path.read_text())
        # JSON2_S: BlastOutput2 -> report -> results -> search -> hits -> hsps
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
        log(f"[TSV] AVISO: no se pudo parsear JSON para descripciones: {e}")

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
            # outfmt6 estándar de 12 columnas; si NCBI devuelve más/menos, se adapta sin inventar
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
    log(f"[TSV] {out} con {n} hits (original, sin filtrar).")
    if n < int(HITLIST_SIZE):
        log(f"[TSV] NOTA: se pidieron {HITLIST_SIZE} hits pero la API devolvió {n}. "
            "Límite de la API (DESCRIPTIONS/ALIGNMENTS o truncado del servidor). No se simulan faltantes.")
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
    log(f"[FILTRO] E-value<=100 y cobertura>=70%: {kept}/{total} -> {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", default=str(FASTA_DEFAULT))
    ap.add_argument("--email", default="student@example.org",
                    help="Email de contacto (pauta NCBI). Reemplazar por el real.")
    ap.add_argument("--rid", default=None, help="Reanudar un RID existente sin re-enviar PUT.")
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
        log(f"Si el script se interrumpe, reanudar con: python3 {Path(__file__).name} --rid {rid}")
        # Primera espera: RTOE es estimación; el polling ya espera 60 s entre intentos
        if rtoe and rtoe > 60:
            log(f"RTOE={rtoe}s estimado por NCBI; el polling consultará cada 60 s (puede tardar).")

    poll_until_ready(rid, args.email)
    files = download_results(rid)
    tsv = build_tsv(files, QUERY_LEN)
    filtrar_e100_cov70(tsv)
    log("Listo. Revisar resultados/blast_vii.tsv y resultados/blast_vii_filtrado_e100_cov70.tsv")


if __name__ == "__main__":
    sys.exit(main())
