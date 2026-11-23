# Tablas de resultados

**Tabla principal** (CPU: mediana de las repeticiones; memoria: pico adicional medido con tracemalloc).

| n | CPU A (ms) | CPU B (ms) | CPU C (ms) | Mem. A (KiB) | Mem. B (KiB) | Mem. C (KiB) |
|---|---|---|---|---|---|---|
| 8 | 0,103 | 0,0205 | 0,00734 | 0,7 | 0,9 | 1,7 |
| 12 | 3,96 | 0,0412 | 0,0137 | 0,9 | 1,0 | 2,6 |
| 16 | 734 | 0,0579 | 0,0224 | 1,2 | 1,1 | 3,8 |
| 20 | 3 156 | 0,0949 | 0,0324 | 1,3 | 1,2 | 5,3 |
| 100 | > 10 000 | 1,62 | 0,725 | — | 3,2 | 87,0 |
| 250 | — | 8,81 | 4,19 | — | 6,9 | 510 |
| 500 | — | 36,8 | 19,2 | — | 13,3 | 2 139 |
| 1000 | — | 161 | 85,9 | — | 58,6 | 11 729 |
| 2000 | — | 750 | 359 | — | 145 | 54 682 |

— : no ejecutada (el tamaño anterior ya superó el límite de tiempo). > 10 000 : no terminó en el límite de tiempo.

**Operaciones** (llamadas recursivas en A; celdas de tabla evaluadas en B y C).

| n | Llamadas A | Celdas B | Celdas C | Celdas B / Celdas C | Longitud LCS |
|---|---|---|---|---|---|
| 8 | 961 | 120 | 64 | 1,88 | 4 |
| 12 | 36 699 | 280 | 144 | 1,94 | 7 |
| 16 | 7 036 278 | 496 | 256 | 1,94 | 7 |
| 20 | 31 088 102 | 789 | 400 | 1,97 | 12 |
| 100 | — | 19 939 | 10 000 | 1,99 | 64 |
| 250 | — | 124 791 | 62 500 | 2,00 | 165 |
| 500 | — | 499 590 | 250 000 | 2,00 | 323 |
| 1000 | — | 1 999 125 | 1 000 000 | 2,00 | 645 |
| 2000 | — | 7 998 280 | 4 000 000 | 2,00 | 1 293 |
