# LCS: tres versiones (recursiva, Hirschberg, programación dinámica)

Actividad individual 1 · Diseño avanzado de algoritmos.
Cálculo de la subsecuencia común más larga (LCS) de dos cadenas con tres estrategias
y comparación de tiempo de CPU y memoria.

| Versión | Archivo | Estrategia | Tiempo | Espacio |
|---|---|---|---|---|
| A | `lcs_recursiva.py` | Recursiva directa, sin memorización | O(2^(m+n)) | O((m+n)·min(m,n)) |
| B | `lcs_hirschberg.py` | Divide y conquista (Hirschberg) | Θ(m·n) | O(min(m,n) + log m) |
| C | `lcs_dinamica.py` | Programación dinámica tabular | Θ(m·n) | Θ(m·n) |

## Requisitos

- Python 3.9 o superior (probado con 3.12). Solo biblioteca estándar.
- `matplotlib` es **opcional**: solo se usa para dibujar la gráfica
  (`pip install matplotlib`). Sin él se generan igualmente los datos y las tablas.

## Ejecución (un único comando)

```
python run_all.py        # en Windows
python3 run_all.py       # en Linux / macOS
```

Ejecuta en orden: 1) pruebas unitarias (`test_lcs.py`), 2) experimentos (`benchmark.py`),
3) tablas y gráfica (`informe.py`). Duración aproximada: 2 minutos.

Salidas:

- `datos/pareja_n<N>.txt`: las parejas de cadenas usadas (semilla fija, reproducibles).
- `resultados/resultados.csv`: tiempo de CPU, pico de memoria, operaciones y longitud de la LCS.
- `resultados/tablas.md`: tablas listas para pegar en la memoria.
- `resultados/grafica_comparativa.png`: tiempo y memoria frente a n (escala log-log).
- `resultados/entorno.txt`: versión de Python, sistema y parámetros del experimento.

## Opciones

```
python benchmark.py --tamanos 8 12 16 100 500 1000 --limite-a 10 --repeticiones 3
python informe.py	# rehace tablas y gráfica a partir de resultados/resultados.csv
python comprobacion_memoria_b.py  # memoria de B con filas array('H')
python -m unittest -v test_lcs
```

## Metodología de medida (resumen)

- **Tiempo**: `time.process_time()` (CPU), mediana de varias repeticiones; las ejecuciones
  cortas se repiten en bucle hasta superar ~0,5 s por muestra. Sin `tracemalloc` activo.
- **Memoria**: pico adicional de memoria asignada por Python (`tracemalloc`), en una pasada aparte.
- **Versión A**: se ejecuta en un proceso aparte con límite de tiempo (10 s por defecto);
  al primer tamaño que lo supera, los mayores se omiten.
- **Validación**: todas las versiones deben coincidir en la longitud de la LCS (y A y C, en la cadena).
