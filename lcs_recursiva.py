"""Versión A - LCS recursivo directo (sin memorización).

Recurrencia sobre los prefijos a[:i] y b[:j]:

    LCS(i, j) = ""                                   si i = 0 o j = 0
    LCS(i, j) = LCS(i-1, j-1) + a[i-1]               si a[i-1] == b[j-1]
    LCS(i, j) = la más larga de LCS(i-1, j), LCS(i, j-1)   en otro caso

Cada subproblema (i, j) se vuelve a resolver una y otra vez, por lo que
el coste es exponencial (ver análisis en la memoria).
"""


def lcs_recursiva_stats(a: str, b: str) -> tuple[str, int]:
    """Devuelve (subsecuencia común más larga, número de llamadas recursivas)."""
    llamadas = 0

    def lcs(i: int, j: int) -> str:
        nonlocal llamadas
        llamadas += 1
        # Caso base: algún prefijo vacío
        if i == 0 or j == 0:
            return ""
        # Los últimos símbolos coinciden: forman parte de la LCS
        if a[i - 1] == b[j - 1]:
            return lcs(i - 1, j - 1) + a[i - 1]
        # No coinciden: se descarta el último símbolo de a o el de b
        sin_a = lcs(i - 1, j)
        sin_b = lcs(i, j - 1)
        return sin_a if len(sin_a) >= len(sin_b) else sin_b

    return lcs(len(a), len(b)), llamadas


def lcs_recursiva(a: str, b: str) -> str:
    """Devuelve una subsecuencia común más larga de a y b."""
    return lcs_recursiva_stats(a, b)[0]


if __name__ == "__main__":
    import random
    import time

    resultado = lcs_recursiva("ABCBDAB", "BDCABA")
    print(f"LCS('ABCBDAB', 'BDCABA') = {resultado!r} (longitud {len(resultado)})")

    print("\nCrecimiento con n (dos cadenas aleatorias de longitud n, alfabeto ACGT):")
    print(f"{'n':>3} {'llamadas':>12} {'tiempo (s)':>11} {'|LCS|':>6}")
    random.seed(1)
    for n in range(6, 17, 2):
        x = "".join(random.choice("ACGT") for _ in range(n))
        y = "".join(random.choice("ACGT") for _ in range(n))
        t0 = time.process_time()
        lcs, llamadas = lcs_recursiva_stats(x, y)
        t = time.process_time() - t0
        print(f"{n:>3} {llamadas:>12} {t:>11.4f} {len(lcs):>6}")
