"""Versión C - LCS con programación dinámica tabular.
  1. Planteamiento: el problema cumple el principio de optimalidad.
  2. Definición recursiva de la longitud de la solución:
        L[i][j] = 0                             si i = 0 o j = 0
        L[i][j] = L[i-1][j-1] + 1               si a[i-1] == b[j-1]
        L[i][j] = max(L[i-1][j], L[i][j-1])     en otro caso
  3. Cálculo de la tabla de (m+1) x (n+1) celdas, de arriba abajo y de
     izquierda a derecha: cada subproblema se resuelve una sola vez.
  4. Construcción de la solución por retroceso desde L[m][n].
Coste: tiempo Θ(m*n), espacio Θ(m*n).
"""


def lcs_dinamica_stats(a: str, b: str) -> tuple[str, dict]:
    """Devuelve (LCS, estadísticas).
    Estadísticas: 'celdas' = celdas de tabla calculadas (m*n),
    'retroceso' = pasos dados al reconstruir la solución (<= m + n).
    """
    m, n = len(a), len(b)

    # Pasos 2 y 3: rellenar la tabla
    L = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        fila, anterior = L[i], L[i - 1]
        ai = a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                fila[j] = anterior[j - 1] + 1
            else:
                arriba, izquierda = anterior[j], fila[j - 1]
                fila[j] = arriba if arriba >= izquierda else izquierda

    # Paso 4: reconstrucción por retroceso desde L[m][n]
    i, j, pasos = m, n, 0
    salida: list[str] = []
    while i > 0 and j > 0:
        pasos += 1
        if a[i - 1] == b[j - 1]:
            salida.append(a[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:  # mismo desempate que la Versión A
            i -= 1
        else:
            j -= 1
    salida.reverse()
    return "".join(salida), {"celdas": m * n, "retroceso": pasos}


def lcs_dinamica(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""
    return lcs_dinamica_stats(a, b)[0]

if __name__ == "__main__":
    r = lcs_dinamica("ABCBDAB", "BDCABA")
    print(f"LCS('ABCBDAB', 'BDCABA') = {r!r} (longitud {len(r)})")
