#!/usr/bin/env python3
"""Desafío X: convierte el tabular BLAST vs PDB (outfmt con % positives) a TSV.

Entrada: /home/Leo/Descargas/CXKZKTY6014-Alignment desafio X.txt (RID CXKZKTY6014, 31 hits).
Salidas: resultados/blast_x.tsv + copia cruda resultados/blast_x.tabular_raw.txt.
"""
from pathlib import Path
import csv
import shutil

BASE = Path(__file__).resolve().parent.parent
SRC = Path('/home/Leo/Descargas/CXKZKTY6014-Alignment desafio X.txt')
OUT = BASE / 'resultados' / 'blast_x.tsv'
OUT.parent.mkdir(parents=True, exist_ok=True)

lines = [l for l in SRC.read_text().splitlines() if l.strip() and not l.startswith('#')]
print(f'hits: {len(lines)}')
cols = ['qacc', 'sacc', 'pident', 'alen', 'mismatch', 'gapopen', 'qstart', 'qend',
        'sstart', 'send', 'evalue', 'bitscore', 'ppositives']
rows = [dict(zip(cols, l.split('\t')[:13])) for l in lines]
with OUT.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, delimiter='\t')
    w.writeheader()
    w.writerows(rows)
shutil.copy(SRC, OUT.parent / 'blast_x.tabular_raw.txt')
print(f'OK {OUT} ({len(rows)} hits)')
