#!/usr/bin/env python3
"""Desafío VIII: compara completa (133 aa) vs. mitad (66 aa) vs. cuarto (32 aa).

3 overlays (E vs %id, Score vs %id, Score vs E) + hist de cobertura.
Uso: python3 src/graficos_viii.py [--outdir resultados]
"""
import argparse
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument('--outdir', default='resultados')
OUT = p.parse_args().outdir

full = pd.read_csv('resultados/blast_vii.tsv', sep='\t')
mit = pd.read_csv('resultados/blast_viii_mitad.tsv', sep='\t')
cua = pd.read_csv('resultados/blast_viii_cuarto.tsv', sep='\t')
for df in (full, mit, cua):
    for c in ['max_score', 'total_score', 'query_cover_pct', 'pident', 'acc_len']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['evalue'] = pd.to_numeric(df['evalue'], errors='coerce')
    df['log10E'] = np.log10(df['evalue'].clip(lower=1e-300))
full['tag'] = 'completa (133 aa, nr)'
mit['tag'] = 'mitad (66 aa, clusteredNR)'
cua['tag'] = 'cuarto (32 aa, clusteredNR)'

for name, df in [('FULL', full), ('MITAD', mit), ('CUARTO', cua)]:
    print(f'--- {name} n={len(df)} ---')
    print(f"  E: min={df.evalue.min()} med={df.evalue.median()} max={df.evalue.max()}")
    print(f"  id: min={df.pident.min():.2f} med={df.pident.median():.2f} max={df.pident.max():.2f}")
    print(f"  score: min={df.max_score.min()} med={df.max_score.median()} max={df.max_score.max()}")
    print(f"  E<=1e-10: {(df.evalue <= 1e-10).sum()} | E>10: {(df.evalue > 10).sum()}")
    for a, b in [('pident', 'log10E'), ('pident', 'max_score'), ('max_score', 'log10E')]:
        sp = df[[a, b]].corr(method='spearman').iloc[0, 1]
        pe = df[[a, b]].corr(method='pearson').iloc[0, 1]
        print(f'  {a} vs {b}: spearman={sp:.3f} pearson={pe:.3f}')

plt.rcParams.update({'figure.dpi': 110})
fig, ax = plt.subplots(figsize=(7, 4.8))
for df in (full, mit, cua):
    ax.scatter(df.pident, df.evalue, s=8, alpha=0.45,
               label=f"{df['tag'].iloc[0]} (n={len(df)})")
ax.set_yscale('log')
ax.set_xlabel('% identidad')
ax.set_ylabel('E-value (log)')
ax.set_title('E-value vs. % identidad — completa vs. mitad vs. cuarto')
ax.legend(markerscale=2, fontsize=8)
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_VIII_Evalue_vs_pident_comp.png')
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.8))
for df in (full, mit, cua):
    ax.scatter(df.pident, df.max_score, s=8, alpha=0.45,
               label=f"{df['tag'].iloc[0]} (n={len(df)})")
ax.set_xlabel('% identidad')
ax.set_ylabel('Score (Max Score)')
ax.set_title('Score vs. % identidad — completa vs. mitad vs. cuarto')
ax.legend(markerscale=2, fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_VIII_Score_vs_pident_comp.png')
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.8))
for df in (full, mit, cua):
    ax.scatter(df.max_score, df.evalue, s=8, alpha=0.45,
               label=f"{df['tag'].iloc[0]} (n={len(df)})")
ax.set_yscale('log')
ax.set_xlabel('Score (Max Score)')
ax.set_ylabel('E-value (log)')
ax.set_title('Score vs. E-value — completa vs. mitad vs. cuarto')
ax.legend(markerscale=2, fontsize=8)
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_VIII_Score_vs_Evalue_comp.png')
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.hist([full.query_cover_pct, mit.query_cover_pct, cua.query_cover_pct],
        bins=20, alpha=0.5, label=['completa 133 aa', 'mitad 66 aa', 'cuarto 32 aa'])
ax.set_xlabel('Cobertura del query (%)')
ax.set_ylabel('N° hits')
ax.set_title('Distribución de cobertura — completa vs. mitad vs. cuarto')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_VIII_cobertura_hist.png')
plt.close(fig)
print('figs VIII OK')
