"""Experimentos: tiempo de CPU y pico de memoria de las tres versiones del LCS.

Uso:  python3 benchmark.py [--tamanos 8 12 ...] [--limite-a 10] [--repeticiones 3]

Diseño de la medición
  * Datos: una pareja de cadenas aleatorias de longitud n sobre {A, C, G, T}
    por cada tamaño, con semilla fija (reproducible). Se guardan en datos/.
  * Tiempo: time.process_time() (CPU), mediana de varias repeticiones.
    Las ejecuciones muy cortas se repiten en bucle para superar la
    resolución del reloj. Sin tracemalloc activo.
  * Memoria: pico de memoria adicional asignada por Python, con
    tracemalloc, en una pasada aparte (tracemalloc ralentiza la ejecución).
    Las cadenas de entrada se crean antes de empezar a medir.
  * Versión A: se ejecuta en un proceso aparte con límite de tiempo. Al
    primer tamaño que lo supera, los tamaños mayores se omiten.
  * Validación cruzada: todas las versiones deben dar la misma longitud
    (y A y C, la misma cadena).
"""
import argparse
import csv
import gc
import math
import multiprocessing as mp
import os
import platform
import queue
import random
import statistics
import sys
import time
import tracemalloc

from lcs_dinamica import lcs_dinamica_stats
from lcs_hirschberg import lcs_hirschberg_stats
from lcs_recursiva import lcs_recursiva_stats

ALFABETO = "ACGT"
TAMANOS_POR_DEFECTO = [8, 12, 16, 20, 100, 250, 500, 1000, 2000]
CAMPOS = ["n", "version", "estado", "cpu_s", "pico_bytes", "operaciones", "longitud_lcs"]


def generar_pareja(n: int, semilla_base: int = 2026) -> tuple[str, str]:
    """Pareja de cadenas aleatorias de longitud n (determinista para cada n)."""
    rng = random.Random(f"{semilla_base}-{n}")
    a = "".join(rng.choice(ALFABETO) for _ in range(n))
    b = "".join(rng.choice(ALFABETO) for _ in range(n))
    return a, b


def medir_cpu(f, a: str, b: str, repeticiones: int, objetivo_s: float = 0.5):
    """Devuelve (mediana del tiempo de CPU en s, resultado de f(a, b)).

    El tamaño del bucle se calibra con perf_counter (alta resolución) para que
    cada muestra dure >= objetivo_s. Así la resolución de process_time (unos
    15,6 ms en Windows) introduce un error relativo pequeño incluso con
    ejecuciones de microsegundos.
    """
    gc.collect()
    w0 = time.perf_counter()
    c0 = time.process_time()
    resultado = f(a, b)
    reloj = time.perf_counter() - w0
    cpu_primera = time.process_time() - c0
    if reloj >= 1.0:             # ejecución larga: una sola muestra basta
        return cpu_primera, resultado

    # Calibración: se duplica el bucle hasta que dure >= 50 ms y se estima el
    # tiempo por ejecución (la primera llamada suele ser más lenta: caché fría).
    bucle = 1
    while True:
        w0 = time.perf_counter()
        for _ in range(bucle):
            f(a, b)
        duracion = time.perf_counter() - w0
        if duracion >= 0.05 or bucle >= 100_000:
            break
        bucle *= 2
    por_ejecucion = duracion / bucle
    bucle = max(1, min(100_000, math.ceil(objetivo_s / max(por_ejecucion, 1e-9))))

    muestras = []
    gc.disable()
    try:
        for _ in range(repeticiones):
            c0 = time.process_time()
            for _ in range(bucle):
                f(a, b)
            muestras.append((time.process_time() - c0) / bucle)
    finally:
        gc.enable()
    return statistics.median(muestras), resultado


def medir_pico(f, a: str, b: str):
    """Devuelve (pico de memoria adicional en bytes durante f(a, b), resultado)."""
    gc.collect()
    tracemalloc.start()
    try:
        resultado = f(a, b)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return pico, resultado


# --- Versión A en un proceso aparte (para poder imponer un límite de tiempo) ---

def _trabajo_a(a, b, modo, repeticiones, cola):
    # La recursión de A llega a profundidad m + n: se amplía el límite de Python
    # para que lo que se mida sea el coste exponencial y no un RecursionError.
    try:
        sys.setrecursionlimit(max(10_000, 2 * (len(a) + len(b)) + 1000))
        if modo == "tiempo":
            valor, (lcs, llamadas) = medir_cpu(lcs_recursiva_stats, a, b, repeticiones)
        else:
            valor, (lcs, llamadas) = medir_pico(lcs_recursiva_stats, a, b)
        cola.put(("ok", lcs, llamadas, valor))
    except Exception as e:  # el padre lo distingue de un timeout
        cola.put(("error", repr(e), None, None))


def _lanzar_a(a, b, modo, repeticiones, limite_s):
    ctx = mp.get_context("spawn")
    cola = ctx.Queue()
    p = ctx.Process(target=_trabajo_a, args=(a, b, modo, repeticiones, cola))
    p.start()
    p.join(limite_s)
    if p.is_alive():             # no ha terminado en el límite: timeout real
        p.terminate()
        p.join()
        return None
    try:
        res = cola.get(timeout=5)
    except queue.Empty:
        raise RuntimeError("El proceso de la Versión A terminó sin devolver resultado")
    if res[0] == "error":
        raise RuntimeError(f"Error en la Versión A: {res[1]}")
    return res[1:]


def ejecutar_a(a, b, limite_s, repeticiones):
    """Devuelve (estado, cpu_s, pico_bytes, llamadas, lcs)."""
    t0 = time.perf_counter()
    res = _lanzar_a(a, b, "tiempo", repeticiones, limite_s)
    if res is None:
        return "timeout", None, None, None, None
    lcs, llamadas, cpu = res
    transcurrido = time.perf_counter() - t0
    res_mem = _lanzar_a(a, b, "memoria", repeticiones, max(limite_s, 10 * transcurrido))
    pico = res_mem[2] if res_mem is not None else None
    return "ok", cpu, pico, llamadas, lcs


# --- Programa principal ---

def guardar_pareja(directorio, n, a, b):
    os.makedirs(directorio, exist_ok=True)
    with open(os.path.join(directorio, f"pareja_n{n}.txt"), "w", encoding="utf-8") as f:
        f.write(a + "\n" + b + "\n")


def escribir_entorno(ruta, args):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"Python: {platform.python_version()} ({platform.python_implementation()})\n")
        f.write(f"Sistema: {platform.system()} {platform.release()}\n")
        f.write(f"Procesador: {platform.processor() or platform.machine()}\n")
        f.write(f"Núcleos lógicos: {os.cpu_count()}\n")
        f.write(f"Tamaños: {args.tamanos}\n")
        f.write(f"Repeticiones: {args.repeticiones}\n")
        f.write(f"Límite de tiempo de la Versión A: {args.limite_a} s\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tamanos", type=int, nargs="+", default=TAMANOS_POR_DEFECTO)
    ap.add_argument("--limite-a", type=float, default=10.0, help="límite de tiempo (s) de la Versión A")
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--salida", default="resultados")
    ap.add_argument("--datos", default="datos")
    args = ap.parse_args(argv)
    args.tamanos = sorted(args.tamanos)

    os.makedirs(args.salida, exist_ok=True)
    escribir_entorno(os.path.join(args.salida, "entorno.txt"), args)
    filas = []
    a_agotada = False

    print(f"{'n':>5} {'ver':>3} {'estado':>8} {'CPU (s)':>10} {'pico (KiB)':>11} {'operaciones':>13} {'|LCS|':>6}")

    def registrar(n, version, estado, cpu=None, pico=None, ops=None, lon=None):
        filas.append({"n": n, "version": version, "estado": estado, "cpu_s": cpu,
                      "pico_bytes": pico, "operaciones": ops, "longitud_lcs": lon})
        cpu_t = f"{cpu:.5f}" if cpu is not None else "-"
        pico_t = f"{pico / 1024:.1f}" if pico is not None else "-"
        print(f"{n:>5} {version:>3} {estado:>8} {cpu_t:>10} {pico_t:>11} "
              f"{ops if ops is not None else '-':>13} {lon if lon is not None else '-':>6}", flush=True)

    for n in args.tamanos:
        a, b = generar_pareja(n)
        guardar_pareja(args.datos, n, a, b)

        # Versiones C y B (en este proceso)
        cpu_c, (lcs_c, est_c) = medir_cpu(lcs_dinamica_stats, a, b, args.repeticiones)
        cpu_b, (lcs_b, est_b) = medir_cpu(lcs_hirschberg_stats, a, b, args.repeticiones)
        assert len(lcs_b) == len(lcs_c), f"B y C difieren en longitud para n={n}"
        pico_c, _ = medir_pico(lcs_dinamica_stats, a, b)
        pico_b, _ = medir_pico(lcs_hirschberg_stats, a, b)

        # Versión A (proceso aparte con límite de tiempo)
        if a_agotada:
            registrar(n, "A", "omitido")
        else:
            estado, cpu_a, pico_a, llamadas, lcs_a = ejecutar_a(a, b, args.limite_a, args.repeticiones)
            if estado == "timeout":
                a_agotada = True
                registrar(n, "A", "timeout")
            else:
                assert lcs_a == lcs_c, f"A y C difieren para n={n}"
                registrar(n, "A", "ok", cpu_a, pico_a, llamadas, len(lcs_a))

        registrar(n, "B", "ok", cpu_b, pico_b, est_b["celdas"], len(lcs_b))
        registrar(n, "C", "ok", cpu_c, pico_c, est_c["celdas"], len(lcs_c))

    ruta = os.path.join(args.salida, "resultados.csv")
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    print(f"\nResultados guardados en {ruta}")
    return ruta


if __name__ == "__main__":
    main()
