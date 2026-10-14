# TP de Alineamientos Secuenciales

Este trabajo práctico analiza resultados de búsquedas BLAST y compara cómo cambian al modificar la longitud de la secuencia o la base de datos consultada.

## Archivos principales

- `secuencia.fasta`: secuencia problema del desafío VII (133 aminoácidos).
- `blast_vii_remote.py`: script para enviar una búsqueda BLASTp a NCBI y guardar los resultados.
- `resultados/`: tablas, archivos de salida y figuras usadas en los informes.
- `src/`: scripts que generan las tablas y los gráficos (ver abajo).
- `informe_desafio_VII.md`, `informe_desafio_VIII.md`, `informe_desafio_IX.md` e `informe_desafio_X.md`: informes de cada desafío.
- `CXJR2NNZ014-Alignment desafio iX .txt`: alineamiento original del desafío IX, correspondiente a LpxA (262 aminoácidos).

Para el desafío VII intenté pedir 20.000 hits a la API de NCBI con los parámetros del script. La búsqueda quedó en estado `WAITING` durante más de 16 horas y no llegó a devolver resultados que pudiera usar. Por eso, las búsquedas analizadas en los informes se hicieron desde la página web de BLAST, que permite solicitar hasta 5.000 hits. Cada tabla contiene la cantidad que devolvió esa búsqueda; por ejemplo, la tabla del desafío VII tiene 1927 hits. Las notas de fuente describen estas limitaciones con más detalle.

## Enunciado

El enunciado de los desafíos está en [Alineamientos secuenciales](https://github.com/AJVelezRueda/Introduccion_a_la_Bioinformatica/blob/master/Teorico_Practicos/Bioinform%C3%A1tica_Primeros_pasos/Alineamientos_secuenciales.md).

## Scripts (`src/`)

Requieren Python 3 con `pandas` y `matplotlib`. Los `parsear_*.py` convierten los
alineamientos web de NCBI (ancho fijo o tabular) a los TSV de `resultados/`;
los `graficos_*.py` calculan correlaciones y generan las figuras
(`--outdir` permite dirigirlas a otra carpeta para no tocar `resultados/`).

```bash
python3 src/parsear_vii.py    # resultados/blast_vii.tsv + filtrado e100_cov70
python3 src/parsear_viii.py   # resultados/blast_viii_mitad.tsv y blast_viii_cuarto.tsv
python3 src/parsear_ix.py     # resultados/blast_ix.tsv
python3 src/parsear_x.py      # resultados/blast_x.tsv
python3 src/graficos_vii.py   # fig_Evalue_vs_pident / fig_Score_vs_pident / fig_Score_vs_Evalue
python3 src/graficos_viii.py  # fig_VIII_*_comp + hist de cobertura
python3 src/graficos_ix.py    # fig_IX_*
python3 src/graficos_x.py     # fig_X_PDB_vs_nr
```

Verificado: los `parsear_*.py` reproducen los TSV commiteados byte por byte
(md5) y los `graficos_*.py` las correlaciones de los informes.
