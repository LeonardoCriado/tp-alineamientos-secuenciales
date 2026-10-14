#!/usr/bin/env python3
"""Desafío X: overlay Score vs. %id de PDB (31 hits) sobre el fondo de nr (5000).

Uso: python3 src/graficos_x.py [--outdir resultados]
"""
import argparse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--outdir', default='resultados')
OUT = p.parse_args().outdir

nr = pd.read_csv('resultados/blast_ix.tsv', sep='\t')
pdb = pd.read_csv('resultados/blast_x.tsv', sep='\t')
for df in (nr, pdb):
    df['pident'] = pd.to_numeric(df['pident'], errors='coerce')
    df['evalue'] = pd.to_numeric(df['evalue'], errors='coerce')
nr['score'] = pd.to_numeric(nr['max_score'], errors='coerce')
pdb['score'] = pd.to_numeric(pdb['bitscore'], errors='coerce')

plt.rcParams.update({'figure.dpi': 110})
fig, ax = plt.subplots(figsize=(7, 4.8))
ax.scatter(nr.pident, nr.score, s=5, alpha=0.25, label=f'nr (n={len(nr)})')
ax.scatter(pdb.pident, pdb.score, s=28, alpha=0.85, marker='D', label=f'PDB (n={len(pdb)})')
ax.set_xlabel('% identidad')
ax.set_ylabel('Score (bits)')
ax.set_title('X: Score vs. %id — PDB sobre el fondo de nr (misma query LpxA)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_X_PDB_vs_nr.png')
plt.close(fig)
print('fig X OK')
