# Desafío VIII — Query completa vs. mitad vs. cuarto

Fragmentos verificados en los alineamientos: mitad = 66 aa N-terminales (`VVGGL...NITIKQ`), cuarto = 32 aa N-terminales (`VVGGL...RYYRE`), ambos prefijos exactos de la secuencia problema (133 aa).

| Query | RID web | Longitud | Base | Hits tabla |
|---|---|---|---|---|
| Completa | CV1UE1Z8014 | 133 aa | nr | 1927 (`resultados/blast_vii.tsv`) |
| Mitad | CXHB5NFK016 | 66 aa | ClusteredNR | 665 (`resultados/blast_viii_mitad.tsv`) |
| Cuarto | CXHPJ65D014 | 32 aa | ClusteredNR | 279 (`resultados/blast_viii_cuarto.tsv`) |

Advertencia: completa usó `nr` y las cortas `ClusteredNR` (colapsa redundancia), así que los N de hits no son estrictamente comparables; las tendencias de score/E-value sí lo son.

Resumen numérico (mediana entre paréntesis):

| | E-value (med) | %id (med) | Max Score (med) | Cobertura (med) | E<=1e-10 | E>10 |
|---|---|---|---|---|---|---|
| Completa | 1e-94–84 (1e-71) | 19–100 (88,1) | 36–285 (224) | 70–100 (95) | 91,1% | 0,9% |
| Mitad | 4e-42–997 (7e-4) | 24–100 (45,3) | 29–144 (47) | 21–100 (89) | 25,6% | 34,1% |
| Cuarto | 8e-14–986 (3e-6) | 38–100 (88,0) | 28–69 (51) | 38–100 (78) | 9,7% | 37,6% |

Correlaciones (Spearman): %id–log10E: −0,821 / −0,725 / −0,840; %id–score: +0,808 / +0,723 / +0,846; score–log10E: −0,999 / −0,997 / −0,994 (completa/mitad/cuarto).

![E-value vs. %id](resultados/fig_VIII_Evalue_vs_pident_comp.png)
![Score vs. %id](resultados/fig_VIII_Score_vs_pident_comp.png)
![Score vs. E-value](resultados/fig_VIII_Score_vs_Evalue_comp.png)
![Cobertura](resultados/fig_VIII_cobertura_hist.png)

## 1. E-value vs. %id

La forma se conserva (nube decreciente en log), pero se desplaza hacia arriba al acortar: el mejor E pasa de 1e-94 a 4e-42 a 8e-14. Cada mitad de longitud cuesta decenas de órdenes de magnitud, lo esperado por Karlin-Altschul (E ~ K·m·n·e^(−λS), con S proporcional a la longitud). El gráfico del cuarto "flota" completo sobre el de la completa: un 100% id que en 133 aa da E~1e-94 en 32 aa solo llega a E~1e-13. Además crece la cola de ruido: E>10 pasa de 0,9% a ~35–38% (transportadores ABC, reguladores bacterianos con E~100–1000 que en la corrida completa ni aparecían o quedaban abajo).

## 2. Score vs. %id

El score máximo escala linealmente con la longitud: 285/144/69 ≈ 2,15 bits por residuo en los tres casos. La pendiente se conserva pero el rango se comprime (eje Y: 36–285 vs. 28–69), así que el poder de separación colapsa: en el cuarto, un prión real (score ~68) y un falso positivo (score ~28–35) se separan por apenas ~2x, contra ~8x en la completa. La señal taxonómica del tope se mantiene (prión humano/bovino/ovino al frente en los tres), pero el "margen de seguridad" desaparece.

## 3. Score vs. E-value

Indistinguible en forma entre las tres: recta en log con correlación ≈ −1 siempre. Es la relación matemática score→E-value, independiente de la biología; solo cambia el tramo del eje que ocupa cada query (285→1e-94 vs. 69→8e-14). Confirma que E-value y score ordenan igual dentro de cada corrida, pero los valores absolutos no son comparables entre longitudes.

## Conclusiones

1. Acortar el query degrada exponencialmente la significancia: el mejor E pierde ~50 órdenes (133→66 aa) y ~28 más (66→32 aa); la fracción con E<=1e-10 cae 91% → 26% → 10%.
2. El score máximo es proporcional a la longitud (~2,15 bits/aa); sirve para normalizar, pero con 32 aa el rango útil es tan chico que verdaderos y espurios se mezclan.
3. Las tres relaciones cualitativas no cambian (solo se trasladan/comprimen): el efecto de longitud es cuantitativo, no un régimen distinto.
4. La cobertura se ensancha hacia abajo (mín 70→21→38, med 95→89→78): con queries cortos aparecen más alineamientos parciales.
5. La mención "prion" en descripción cae 90% → 45–61% y el ruido de E alto domina la cola: con 1/4 de secuencia el top sigue siendo prión, pero el resto del listado deja de ser interpretable como homología.
6. Regla práctica: fragmentos cortos sirven para confirmar una identidad ya sospechada (el top hit resiste), no para descubrir homólogos lejanos; para eso hace falta longitud, y los cortes de E deben endurecerse al acortar (E<=100, pedido en el VII, aquí dejaría pasar ~1/3 de ruido con E>10).
