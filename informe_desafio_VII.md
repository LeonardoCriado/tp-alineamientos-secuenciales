# Desafío VII — Relación entre E-value, identidad y score

Para este análisis usé `resultados/blast_vii.tsv`, que reúne 1927 hits de BLASTP contra nr para una secuencia problema de 133 aminoácidos (RID web CV1UE1Z8014 y CSV de la API del mismo RID).

El filtro solicitado fue E-value ≤ 100 y cobertura ≥ 70%. Los 1927 hits cumplen ambas condiciones: el E-value máximo es 84 y la cobertura mínima es 70%. En este caso, aplicar el filtro no elimina filas. Los rangos son: E-value de 1e-94 a 84, identidad de 19,13% a 100% y Max Score de 36,2 a 285. Las notas de fuente detallan qué se pudo recuperar y qué límites tiene la tabla.

Correlaciones (n = 1927):

- Identidad y log10(E-value): Spearman −0,821; Pearson −0,972.
- Identidad y score: Spearman +0,808; Pearson +0,970.
- Score y log10(E-value): Spearman −0,999; Pearson −1,000.

![E-value vs. % identidad](resultados/fig_Evalue_vs_pident.png)
![Score vs. % identidad](resultados/fig_Score_vs_pident.png)
![Score vs. E-value](resultados/fig_Score_vs_Evalue.png)

## E-value e identidad

En general, los hits con mayor porcentaje de identidad tienen E-values menores. En el gráfico, esta tendencia se ve como una caída de varios órdenes de magnitud en el eje logarítmico. Por ejemplo, los hits con 100% de identidad tienen E-values cercanos a 1e-94; alrededor de 90% se encuentran cerca de 1e-80, mientras que entre 20% y 25% aparecen valores de 1 a 84.

Para un mismo porcentaje de identidad hay cierta dispersión. Esto es esperable porque el E-value también depende de la longitud y la calidad del alineamiento y del tamaño de la base de datos. Por eso, identidad y E-value están relacionados, pero no hay una correspondencia única entre ambos.

## Score e identidad

El score tiende a aumentar junto con la identidad (Pearson +0,970). En la parte alta, los valores se agrupan cerca de 280–285, sobre todo para hits con 99–100% de identidad y cobertura completa. Para identidades menores al 40%, los scores van aproximadamente de 36 a 90 y están más dispersos.

El porcentaje de identidad cuenta las posiciones iguales, mientras que el score también considera las sustituciones y los gaps según el sistema de puntuación. Por eso, dos alineamientos con la misma identidad pueden tener scores distintos.

## Score y E-value

La correlación entre score y log10(E-value) es casi −1. En estos resultados, los scores más altos se asocian con E-values más bajos, de acuerdo con la relación esperada entre score y significancia estadística en BLAST. El tamaño de la base de datos también influye en el E-value, así que este aporta contexto que el score por sí solo no muestra.

## Lectura biológica y límites

Los hits de mayor identidad corresponden a proteínas priónicas de mamíferos: se observan secuencias idénticas de humano y valores altos en otros primates y mamíferos. A medida que baja la identidad aparecen también alineamientos con proteínas de otros grupos. La tabla incluye hits con E-values altos, por lo que esos resultados no alcanzan por sí solos para afirmar homología funcional.

El filtro E-value ≤ 100 y cobertura ≥ 70% deja pasar todos los hits de esta tabla, incluidos los de E-value entre 61 y 84. Para interpretar los hits como posibles homólogos conviene considerar en conjunto la significancia, la identidad, la cobertura y el organismo de origen. Además, la tabla recuperada no alcanza los 20.000 hits pedidos en los parámetros de la corrida; las notas de fuente explican esta limitación.
