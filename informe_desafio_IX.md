# Desafío IX — Identificación de la proteína problema (262 aa)

Fuente: `CXJR2NNZ014-Alignment desafio iX .txt` (BLASTP vs nr, query 262 aa, RID CXJR2NNZ014). Verifiqué que el query del archivo es idéntico al enunciado (reconstrucción de los HSP = 262/262 residuos) y el primer alineamiento detallado muestra identidad total a lo largo de toda la secuencia con Expect 0.0. Tabla parseada sin filtrar a `resultados/blast_ix.tsv` (5000 hits).

## Identidad: acil-ACP–UDP-N-acetilglucosamina O-aciltransferasa (LpxA)

- Proteína: **acyl-ACP–UDP-N-acetylglucosamine O-acyltransferase**, gen `lpxA`, EC 2.3.1.129 — primera enzima de la vía de Raetz (biosíntesis del lípido A, componente del lipopolisacárido de Gram-negativos).
- Evidencia: 4714/5000 hits (94%) anotados con ese nombre (4085 + 629 MULTISPECIES); top hit `WP_000565966.1` con 100% identidad, 100% cobertura, score 533, E=0.0. Estructuras cristalográficas entre los top (cadenas `2JF2_A`, `7OKC_A` de *E. coli*).
- Origen más probable del query: *Escherichia coli* (taxid 562, 693 hits; el resto son enterobacterias cercanas: *Klebsiella* 573, *Salmonella* 28901, *Vibrio* 666).
- Fuerza de la asignación: el peor hit de los 5000 tiene E=2e-108 y 57% identidad — los 5000 son homólogos significativos, sin cola de ruido. No hay ambigüedad posible.

## Comportamiento E-value vs. %id, Score vs. %id, Score vs. E-value (n=5000)

Rangos: E 0.0–2e-108 (805 con E=0.0, todos E<=1e-10); %id 57–100 (mediana alta, 2467 con id>=90); score 322–533; cobertura 61–100 (4492 con 100%).

Correlaciones: %id–log10E Spearman −0,872; %id–score +0,871; score–log10E Spearman −0,998. Mismo patrón de los desafíos VII–VIII: el E cae en log con %id, el score crece con %id, y score–log(E) es casi determinista. Detalle: el Pearson score–log(E) baja a −0,803 solo por el piso de E=0.0 (805 puntos clavados en 1e-300 tras el clipping); el orden (Spearman) sigue ≈ −1.

![E-value vs. % identidad](resultados/fig_IX_Evalue_vs_pident.png)
![Score vs. % identidad](resultados/fig_IX_Score_vs_pident.png)
![Score vs. E-value](resultados/fig_IX_Score_vs_Evalue.png)

A diferencia del VII (prión eucariota con cola de ruido bacteriano hasta E=84), aquí no hay fondo espurio: la proteína es muy conservada en bacterias (mínimo 57% id) y la nube es compacta. El gráfico E vs. %id muestra el "techo" de E=0.0 como línea horizontal de 805 puntos —límite de precisión del reporte, no biología— y por debajo la caída esperada hacia 2e-108 en los homólogos más divergentes (p. ej. *Aeromonas*, 58,8% id, score 325, todavía 100% cobertura).
