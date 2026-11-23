"""Versión B - LCS con la estrategia divide y conquista de Hirschberg.
  1. Se divide la cadena a en dos mitades: a1 = a[:mid] y a2 = a[mid:].
  2. En espacio lineal (solo dos filas) se calculan
        L[j] = |LCS(a1, b[:j])|           (puntuaciones directas)
        R[j] = |LCS(a2, b[len(b)-j:])|    (puntuaciones inversas)
  3. El punto de corte k maximiza L[k] + R[n-k]; ese máximo es |LCS(a, b)|.
  4. Se resuelven recursivamente (a1, b[:k]) y (a2, b[k:]) y se concatenan.

Coste: tiempo Θ(m*n), espacio O(min(m, n)+ log m).
No se crean sublistas ni subcadenas de a: se trabaja con índices.
"""


def _fila(a, i0, i1, b, j0, j1, inversa):
    """Última fila de la tabla de LCS de a[i0:i1] frente a b[j0:j1].
    inversa=False: devuelve F[j] = |LCS(a[i0:i1], b[j0:j0+j])|
    inversa=True : devuelve F[j] = |LCS(a[i0:i1], b[j1-j:j1])|
    (se recorren ambas cadenas al revés)
    Solo se mantienen dos filas de longitud n+1.
    """
    bs = b[j0:j1]
    if inversa:
        bs = bs[::-1]
        filas = range(i1 - 1, i0 - 1, -1)
    else:
        filas = range(i0, i1)
    n = len(bs)
    anterior = [0] * (n + 1)
    actual = [0] * (n + 1)
    for i in filas:
        ai = a[i]
        for j in range(1, n + 1):
            if ai == bs[j - 1]:
                actual[j] = anterior[j - 1] + 1
            else:
                arriba = anterior[j]
                izquierda = actual[j - 1]
                actual[j] = arriba if arriba >= izquierda else izquierda
        anterior, actual = actual, anterior
    return anterior


def _punto_corte(a, i0, mid, i1, b, j0, j1):
    """Devuelve k tal que L[k] + R[n-k] es máximo.
    L y R son locales: se liberan al volver, antes de recursar,
    para no acumular O(n) por cada nivel de la recursión.
    """
    n = j1 - j0
    L = _fila(a, i0, mid, b, j0, j1, inversa=False)
    R = _fila(a, mid, i1, b, j0, j1, inversa=True)
    mejor_k, mejor = 0, -1
    for k in range(n + 1):
        suma = L[k] + R[n - k]
        if suma > mejor:
            mejor, mejor_k = suma, k
    return mejor_k


def _hirschberg(a, i0, i1, b, j0, j1, salida, est, nivel):
    m = i1 - i0
    n = j1 - j0
    est["prof_max"] = max(est["prof_max"], nivel)
    if m == 0 or n == 0:
        return
    if m == 1:  # caso base: un solo símbolo de a
        est["celdas"] += n
        c = a[i0]
        for j in range(j0, j1):
            if b[j] == c:
                salida.append(c)
                return
        return
    mid = i0 + m // 2
    est["celdas"] += m * n  # (mid-i0)*n filas directas + (i1-mid)*n inversas
    k = _punto_corte(a, i0, mid, i1, b, j0, j1)
    _hirschberg(a, i0, mid, b, j0, j0 + k, salida, est, nivel + 1)
    _hirschberg(a, mid, i1, b, j0 + k, j1, salida, est, nivel + 1)


def lcs_hirschberg_stats(a: str, b: str) -> tuple[str, dict]:
    """Devuelve (LCS, estadísticas).
    Estadísticas: 'celdas' = celdas de tabla evaluadas en total,
    'prof_max' = profundidad máxima de la recursión.
    """
    # La cadena más corta va en el eje de las filas: espacio O(min(m, n)).
    if len(b) > len(a):
        a, b = b, a
    est = {"celdas": 0, "prof_max": 0}
    salida: list[str] = []
    _hirschberg(a, 0, len(a), b, 0, len(b), salida, est, 1)
    return "".join(salida), est


def lcs_hirschberg(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""
    return lcs_hirschberg_stats(a, b)[0]

if __name__ == "__main__":
    r = lcs_hirschberg("ABCBDAB", "BDCABA")
    print(f"LCS('ABCBDAB', 'BDCABA') = {r!r} (longitud {len(r)})")
