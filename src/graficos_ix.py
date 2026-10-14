#!/usr/bin/env python3
"""Desafío IX: correlaciones + 3 scatter de LpxA vs nr (n=5000).

Uso: python3 src/graficos_ix.py [--outdir resultados]
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

df = pd.read_csv('resultados/blast_ix.tsv', sep='\t')
for c in ['max_score', 'total_score', 'query_cover_pct', 'pident', 'acc_len']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['evalue'] = pd.to_numeric(df['evalue'], errors='coerce')
df = df[df.evalue.notna()]
df['log10E'] = np.log10(df['evalue'].clip(lower=1e-300))
print(f'n={len(df)} E:[{df.evalue.min()},{df.evalue.max()}] '
      f'id:[{df.pident.min()},{df.pident.max()}] score:[{df.max_score.min()},{df.max_score.max()}]')
for a, b in [('pident', 'log10E'), ('pident', 'max_score'), ('max_score', 'log10E')]:
    sp = df[[a, b]].corr(method='spearman').iloc[0, 1]
    pe = df[[a, b]].corr(method='pearson').iloc[0, 1]
    print(f'{a} vs {b}: spearman={sp:.3f} pearson={pe:.3f}')

plt.rcParams.update({'figure.dpi': 110})
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(df.pident, df.evalue, s=6, alpha=0.4)
ax.set_yscale('log')
ax.set_xlabel('% identidad')
ax.set_ylabel('E-value (log)')
ax.set_title('IX: E-value vs. % identidad (n=5000, BLASTP nr)')
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_IX_Evalue_vs_pident.png')
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(df.pident, df.max_score, s=6, alpha=0.4)
ax.set_xlabel('% identidad')
ax.set_ylabel('Score (Max Score)')
ax.set_title('IX: Score vs. % identidad (n=5000)')
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_IX_Score_vs_pident.png')
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(df.max_score, df.evalue, s=6, alpha=0.4)
ax.set_yscale('log')
ax.set_xlabel('Score (Max Score)')
ax.set_ylabel('E-value (log)')
ax.set_title('IX: Score vs. E-value (n=5000)')
ax.grid(True, which='both', alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUT}/fig_IX_Score_vs_Evalue.png')
plt.close(fig)
print('figs IX OK')
