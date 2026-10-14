# Desafío X — BLASTp contra PDB (misma secuencia del IX, RID CXKZKTY6014)

Fuente: `/home/Leo/Descargas/CXKZKTY6014-Alignment desafio X.txt` (tabular outfmt con `% positives`), 31 hits. Guardado como `resultados/blast_x.tsv` (+ copia cruda `blast_x.tabular_raw.txt`). Comparación contra `resultados/blast_ix.tsv` (nr, 5000 hits).

Rangos PDB: E 0.0–92 (18 con E<=1e-10, 8 con E>1); %id 22–100; score 26–533; cobertura query 10–100%. Verificado en RCSB: `1LXA` = LpxA de *E. coli* K-12 (gen `lpxA`, EC 2.3.1.129, Raetz & Roderick 1995); `8E62` = N-acetiltransferasa Pcryo_0615 de *Psychrobacter cryohalolentis* (otra vía de azúcares nucleotídicos, mismo plegamiento).

![PDB sobre fondo nr](resultados/fig_X_PDB_vs_nr.png)

## ¿Se obtienen los mismos resultados?

La identificación sí es la misma (LpxA, top hits 100% id / E=0.0 / score 533: `1LXA_A`, `2JF2_A`, `7OKC_A`, `6P9P_A`), pero el listado no: 31 hits contra 5000 de nr. PDB es un subconjunto diminuto y sesgado de nr (solo proteínas con estructura resuelta), así que desaparece la diversidad taxonómica (miles de LpxA bacterianas idénticas en secuencia colapsan a unas pocas cadenas cristalizadas) y el E-value mínimo informativo se pierde entre tanto 0.0. Como buscador de homólogos es mucho menos sensible; como anotador funcional/estructural es más directo.

## ¿Qué tipo de hits se recuperan?

Cuatro capas, legibles en la tabla:

1. La misma proteína cristalizada varias veces: `1LXA_A`, `2JF2_A`, `7OKC_A`, `6P9P_A` (100% id, cobertura 100%, E=0.0).
2. Ortólogos estructurales (misma función, otra especie): `6OSS_A` (72,7%), y el bloque ~41–54% (`4EQY_A`, `4E6U_A`, `5JXX_A`, `5DEM_A`, `1J2Z_A`...), todos con E<=1e-55 y cobertura casi total.
3. Homólogos remotos de la superfamilia (mismo plegamiento LβH de hexapéptidos, otra función): `8E62_A` (27,3% id pero E=2,7e-17 en 220 aa: N-acetiltransferasa de otra vía), `2IU8_A`, `4E75_A` (E~1e-9/1e-10). Son los hits más informativos del modo PDB: la secuencia sola parece ruido (~27% id) y la estructura revela parentesco.
4. Ruido: 8 hits con E>1 (hasta 92), alineamientos cortos y parciales (cobertura 10–70%, p. ej. `1B7K_A`, `6NPJ_B`, `2Z4H_A`, ribosomales `30DR_W`/`5AFU_V`/`5ADX_V` con 41 aa). Se descartan por E-value, como siempre.

## ¿Cuándo es útil este modo?

- Confirmar la función con evidencia estructural: si el query pega 100% a una cadena PDB anotada (`1LXA`), la asignación LpxA queda cerrada sin inferencia.
- Elegir molde para modelado por homología (los ortólogos al 40–70% son moldes ideales) y localizar sitio activo, ligandos y residuos catalíticos por superposición.
- Detectar el plegamiento/familia cuando la identidad es baja: el caso `8E62_A` muestra que PDB rescata relaciones de superfamilia invisibles en el ruido de nr.
- No sirve para: censos taxonómicos, encontrar el homólogo más cercano en secuencia, ni descubrir genes nuevos — para eso nr es insustituible. Regla: nr para identificar y medir distancia evolutiva; PDB para pasar de secuencia a estructura y mecanismo.
