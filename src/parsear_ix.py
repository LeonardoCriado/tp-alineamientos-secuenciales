#!/usr/bin/env python3
"""Desafío IX: parsea la tabla web de NCBI (LpxA, 262 aa, BLASTP vs nr) a TSV.

Entrada: CXJR2NNZ014-Alignment desafio iX .txt (RID CXJR2NNZ014, junto al script).
Salida: resultados/blast_ix.tsv (5000 hits, sin filtrar).
"""
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / 'CXJR2NNZ014-Alignment desafio iX .txt'
OUT = BASE / 'resultados' / 'blast_ix.tsv'
OUT.parent.mkdir(parents=True, exist_ok=True)

lines = SRC.read_text(encoding='utf-8', errors='replace').splitlines()
i0 = next(i for i, l in enumerate(lines) if l.startswith('Sequences producing significant'))
iA = next((i for i, l in enumerate(lines) if l.strip() == 'Alignments:'), len(lines))
data = [l for l in lines[i0 + 3:iA] if l.strip()]
print(f'hits: {len(data)}')

rows = []
for l in data:
    l = l.ljust(169)
    rows.append({
        'accession': l[152:169].strip() or l.split()[-1],
        'descripcion': l[0:66].strip(),
        'nombre_cientifico': l[66:82].strip(),
        'nombre_comun': l[82:98].strip(),
        'taxid': l[98:109].strip(),
        'max_score': l[109:116].strip(),
        'total_score': l[116:122].strip(),
        'query_cover_pct': l[122:128].strip().replace('%', ''),
        'evalue': l[128:134].strip(),
        'pident': l[134:141].strip(),
        'acc_len': l[141:152].strip(),
    })

cols = ['accession', 'descripcion', 'nombre_cientifico', 'nombre_comun', 'taxid',
        'max_score', 'total_score', 'query_cover_pct', 'evalue', 'pident', 'acc_len']
with OUT.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols, delimiter='\t')
    w.writeheader()
    w.writerows(rows)
print(f'OK {OUT} ({len(rows)} hits)')
