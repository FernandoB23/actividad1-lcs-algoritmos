"""Pruebas de validación de las versiones del LCS.
Ejecutar:  python3 -m unittest -v test_lcs
Como pueden existir varias LCS válidas, se comprueba (1) la longitud óptima
y (2) que el resultado es subsecuencia de ambas cadenas.
"""
import random
import unittest

from lcs_recursiva import lcs_recursiva
from lcs_hirschberg import lcs_hirschberg, lcs_hirschberg_stats
from lcs_dinamica import lcs_dinamica, lcs_dinamica_stats


def es_subsecuencia(s: str, t: str) -> bool:
    it = iter(t)
    return all(c in it for c in s)


def longitud_referencia(a: str, b: str) -> int:
    """Referencia independiente (DP de dos filas), solo para los tests."""
    anterior = [0] * (len(b) + 1)
    for x in a:
        actual = [0]
        for j, y in enumerate(b, 1):
            actual.append(anterior[j - 1] + 1 if x == y else max(anterior[j], actual[j - 1]))
        anterior = actual
    return anterior[-1]


def cadena_aleatoria(rng, n, alfabeto):
    return "".join(rng.choice(alfabeto) for _ in range(n))


class TestCasosFijos(unittest.TestCase):
    VERSIONES = {"A": lcs_recursiva, "B": lcs_hirschberg, "C": lcs_dinamica}

    def comprobar(self, a, b, longitud_esperada):
        for nombre, f in self.VERSIONES.items():
            with self.subTest(version=nombre, a=a, b=b):
                r = f(a, b)
                self.assertEqual(len(r), longitud_esperada)
                self.assertTrue(es_subsecuencia(r, a))
                self.assertTrue(es_subsecuencia(r, b))

    def test_ejemplo_clasico(self):
        self.comprobar("ABCBDAB", "BDCABA", 4)

    def test_cadenas_vacias(self):
        self.comprobar("", "", 0)
        self.comprobar("", "ABC", 0)
        self.comprobar("ABC", "", 0)

    def test_cadenas_identicas(self):
        self.comprobar("ACGTACGT", "ACGTACGT", 8)

    def test_alfabetos_disjuntos(self):
        self.comprobar("AAAA", "BBBBB", 0)

    def test_un_solo_simbolo(self):
        self.comprobar("A", "CGTAC", 1)
        self.comprobar("A", "CGTC", 0)
        self.comprobar("CGTAC", "A", 1)

    def test_una_contenida_en_otra(self):
        self.comprobar("ACE", "AXCXEX", 3)
        self.comprobar("AXCXEX", "ACE", 3)


class TestAleatorios(unittest.TestCase):
    def test_A_frente_a_B_cadenas_pequenas(self):
        rng = random.Random(7)
        for _ in range(300):
            alfabeto = rng.choice(["AC", "ACGT"])
            a = cadena_aleatoria(rng, rng.randint(0, 9), alfabeto)
            b = cadena_aleatoria(rng, rng.randint(0, 9), alfabeto)
            ra, rb = lcs_recursiva(a, b), lcs_hirschberg(a, b)
            with self.subTest(a=a, b=b):
                self.assertEqual(len(ra), len(rb))
                self.assertTrue(es_subsecuencia(rb, a) and es_subsecuencia(rb, b))

    def test_B_frente_a_referencia_cadenas_medianas(self):
        rng = random.Random(11)
        for _ in range(200):
            alfabeto = rng.choice(["AC", "ACGT", "ABCDEFGHIJ"])
            a = cadena_aleatoria(rng, rng.randint(0, 120), alfabeto)
            b = cadena_aleatoria(rng, rng.randint(0, 120), alfabeto)
            r = lcs_hirschberg(a, b)
            with self.subTest(a=a, b=b):
                self.assertEqual(len(r), longitud_referencia(a, b))
                self.assertTrue(es_subsecuencia(r, a) and es_subsecuencia(r, b))

    def test_B_es_simetrica_en_longitud(self):
        rng = random.Random(3)
        for _ in range(50):
            a = cadena_aleatoria(rng, rng.randint(1, 80), "ACGT")
            b = cadena_aleatoria(rng, rng.randint(1, 80), "ACGT")
            self.assertEqual(len(lcs_hirschberg(a, b)), len(lcs_hirschberg(b, a)))

    def test_A_y_C_devuelven_la_misma_cadena(self):
        # Mismo desempate en ambas versiones: coinciden cadena a cadena.
        rng = random.Random(13)
        for _ in range(300):
            alfabeto = rng.choice(["AC", "ACGT"])
            a = cadena_aleatoria(rng, rng.randint(0, 9), alfabeto)
            b = cadena_aleatoria(rng, rng.randint(0, 9), alfabeto)
            with self.subTest(a=a, b=b):
                self.assertEqual(lcs_recursiva(a, b), lcs_dinamica(a, b))

    def test_C_frente_a_referencia_cadenas_medianas(self):
        rng = random.Random(17)
        for _ in range(200):
            alfabeto = rng.choice(["AC", "ACGT", "ABCDEFGHIJ"])
            a = cadena_aleatoria(rng, rng.randint(0, 120), alfabeto)
            b = cadena_aleatoria(rng, rng.randint(0, 120), alfabeto)
            r = lcs_dinamica(a, b)
            with self.subTest(a=a, b=b):
                self.assertEqual(len(r), longitud_referencia(a, b))
                self.assertTrue(es_subsecuencia(r, a) and es_subsecuencia(r, b))

    def test_B_y_C_coinciden_en_longitud_cadenas_grandes(self):
        rng = random.Random(19)
        for _ in range(10):
            a = cadena_aleatoria(rng, rng.randint(200, 400), "ACGT")
            b = cadena_aleatoria(rng, rng.randint(200, 400), "ACGT")
            self.assertEqual(len(lcs_hirschberg(a, b)), len(lcs_dinamica(a, b)))


class TestPropiedadesDeB(unittest.TestCase):
    def test_celdas_acotadas_por_2mn_y_profundidad_logaritmica(self):
        rng = random.Random(5)
        a = cadena_aleatoria(rng, 400, "ACGT")
        b = cadena_aleatoria(rng, 300, "ACGT")
        _, est = lcs_hirschberg_stats(a, b)
        m, n = max(len(a), len(b)), min(len(a), len(b))
        self.assertLessEqual(est["celdas"], 2 * m * n + m)
        self.assertLessEqual(est["prof_max"], 12)  # ~ log2(400) + 2


class TestPropiedadesDeC(unittest.TestCase):
    def test_celdas_exactas_y_retroceso_acotado(self):
        rng = random.Random(23)
        a = cadena_aleatoria(rng, 150, "ACGT")
        b = cadena_aleatoria(rng, 90, "ACGT")
        _, est = lcs_dinamica_stats(a, b)
        self.assertEqual(est["celdas"], len(a) * len(b))
        self.assertLessEqual(est["retroceso"], len(a) + len(b))


if __name__ == "__main__":
    unittest.main()
