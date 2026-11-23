"""Python guarda como objetos independientes (28 bytes cada uno) los enteros
mayores de 256. Las filas de la Versión B son listas de enteros que superan ese
valor a partir de n= 400, y eso infla la memoria medida. Aquí se repite la
medición sustituyendo las filas por array('H') (2 bytes por celda) para
separar el efecto del lenguaje del comportamiento del algoritmo.
Uso:  python3 comprobacion_memoria_b.py
"""
from array import array

import lcs_hirschberg
from benchmark import generar_pareja, medir_pico


def _fila_array(a, i0, i1, b, j0, j1, inversa):
    """Igual que lcs_hirschberg._fila, pero con filas array('H')."""
    bs = b[j0:j1][::-1] if inversa else b[j0:j1]
    filas = range(i1 - 1, i0 - 1, -1) if inversa else range(i0, i1)
    n = len(bs)
    anterior = array("H", bytes(2 * (n + 1)))
    actual = array("H", bytes(2 * (n + 1)))
    for i in filas:
        ai = a[i]
        for j in range(1, n + 1):
            if ai == bs[j - 1]:
                actual[j] = anterior[j - 1] + 1
            else:
                arriba, izquierda = anterior[j], actual[j - 1]
                actual[j] = arriba if arriba >= izquierda else izquierda
        anterior, actual = actual, anterior
    return anterior


def main():
    original = lcs_hirschberg._fila
    print(f"{'n':>5} {'lista (KiB)':>12} {'array H (KiB)':>14} {'crecim. lista':>14} {'crecim. array':>14}")
    previo = None
    for n in (100, 250, 500, 1000, 2000):
        a, b = generar_pareja(n)
        pico_lista, (lcs_l, _) = medir_pico(lcs_hirschberg.lcs_hirschberg_stats, a, b)
        lcs_hirschberg._fila = _fila_array
        try:
            pico_array, (lcs_a, _) = medir_pico(lcs_hirschberg.lcs_hirschberg_stats, a, b)
        finally:
            lcs_hirschberg._fila = original
        assert len(lcs_l) == len(lcs_a), "ambas variantes deben dar la misma longitud"
        crec = (f"x{pico_lista / previo[0]:.2f}", f"x{pico_array / previo[1]:.2f}") if previo else ("-", "-")
        print(f"{n:>5} {pico_lista / 1024:>12.1f} {pico_array / 1024:>14.1f} {crec[0]:>14} {crec[1]:>14}")
        previo = (pico_lista, pico_array)


if __name__ == "__main__":
    main()
