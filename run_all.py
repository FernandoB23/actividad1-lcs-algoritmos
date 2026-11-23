"""
Ejecuta, en orden: 1) pruebas unitarias, 2) experimentos, 3) tablas y gráfica.
Los resultados quedan en resultados/ y las parejas de cadenas en datos/.
"""
import subprocess
import sys


def main():
    print("== 1/3 Pruebas unitarias ==", flush=True)
    r = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_lcs"])
    if r.returncode != 0:
        sys.exit("Las pruebas unitarias han fallado: se detiene la ejecución.")

    print("\n== 2/3 Experimentos ==", flush=True)
    import benchmark
    benchmark.main([])

    print("\n== 3/3 Tablas y gráfica ==", flush=True)
    import informe
    informe.main([])


if __name__ == "__main__":
    main()
