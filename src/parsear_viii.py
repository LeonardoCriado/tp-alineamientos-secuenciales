#!/usr/bin/env python3
"""Desafío VIII: parsea las tablas web ClusteredNR (mitad 66 aa y cuarto 32 aa) a TSV.

Entradas: /home/Leo/Descargas/CXHB5NFK016-Alignment mitad.txt (RID CXHB5NFK016),
          /home/Leo/Descargas/CXHPJ65D014-Alignment un cuarto.txt (RID CXHPJ65D014).
Salidas: resultados/blast_viii_mitad.tsv (665 hits), resultados/blast_viii_cuarto.tsv (279 hits).
"""
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parent.parent
OUTDIR = BASE / 'resultados'
OUTDIR.mkdir(parents=True, exist_ok=True)


def parse_clustered(src: Path):
    lines = src.read_text(encoding='utf-8', errors='replace').splitlines()
    i0 = next(i for i, l in enumerate(lines) if 'producing significant' in l)
    iA = next((i for i, l in enumerate(lines) if l.strip() == 'Alignments:'), len(lines))
    data = [l for l in lines[i0 + 3:iA] if l.strip()]
    rows = []
    for l in data:
        l = l.ljust(191)
        rows.append({
            'cluster_rep': l[0:66].strip(),
            'n_mem': l[66:77].strip(),
            'n_taxa': l[77:88].strip(),
            'nombre_cientifico': l[88:104].strip(),
            'cluster_ancestor': l[104:120].strip(),
            'taxid': l[120:131].strip(),
            'max_score': l[131:138].strip(),
            'total_score': l[138:144].strip(),
            'query_cover_pct': l[144:150].strip().replace('%', ''),
            'evalue': l[150:156].strip(),
            'pident': l[156:163].strip(),
            'acc_len': l[163:174].strip(),
            'accession': l[174:191].strip() or l.split()[-1],
        })
    return rows


for src, out in [
    (Path('/home/Leo/Descargas/CXHB5NFK016-Alignment mitad.txt'), OUTDIR / 'blast_viii_mitad.tsv'),
    (Path('/home/Leo/Descargas/CXHPJ65D014-Alignment un cuarto.txt'), OUTDIR / 'blast_viii_cuarto.tsv'),
]:
    rows = parse_clustered(src)
    cols = ['accession', 'cluster_rep', 'n_mem', 'n_taxa', 'nombre_cientifico',
            'cluster_ancestor', 'taxid', 'max_score', 'total_score',
            'query_cover_pct', 'evalue', 'pident', 'acc_len']
    with out.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t')
        w.writeheader()
        w.writerows(rows)
    print(f'OK {out} ({len(rows)} hits)')
