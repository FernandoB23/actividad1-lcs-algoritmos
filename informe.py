"""Tablas y gráficas a partir de resultados/resultados.csv.

Uso:  python3 informe.py [--salida resultados]
Genera: tablas.md (tablas listas para pegar) y grafica_comparativa.png
(la gráfica requiere matplotlib; si no está instalado, solo se generan las tablas).
"""
import argparse
import csv
import os
import re


def leer(ruta_csv):
    datos = {}
    with open(ruta_csv, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            n = int(fila["n"])
            datos.setdefault(n, {})[fila["version"]] = {
                "estado": fila["estado"],
                "cpu_s": float(fila["cpu_s"]) if fila["cpu_s"] else None,
                "pico": int(fila["pico_bytes"]) if fila["pico_bytes"] else None,
                "ops": int(fila["operaciones"]) if fila["operaciones"] else None,
                "lon": int(fila["longitud_lcs"]) if fila["longitud_lcs"] else None,
            }
    return datos


def limite_a(salida):
    try:
        with open(os.path.join(salida, "entorno.txt"), encoding="utf-8") as f:
            m = re.search(r"Versión A: ([\d.]+) s", f.read())
            return float(m.group(1))
    except (OSError, AttributeError):
        return None


def num(x, decimales=0):
    """Formato español: coma decimal y espacio como separador de miles."""
    texto = f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return texto


def cifras(x, significativas=3):
    """x con 'significativas' cifras significativas, en formato español."""
    if x == 0:
        return "0"
    from math import floor, log10
    dec = max(0, significativas - 1 - int(floor(log10(abs(x)))))
    return num(x, dec)


def celda_cpu(r, limite):
    if r is None or r["estado"] == "omitido":
        return "—"
    if r["estado"] == "timeout":
        return f"> {num(limite * 1000)}" if limite else "timeout"
    return cifras(r["cpu_s"] * 1000)


def celda_mem(r):
    if r is None or r["estado"] != "ok" or r["pico"] is None:
        return "—"
    return num(r["pico"] / 1024, 1 if r["pico"] < 100 * 1024 else 0)


def tabla_principal(datos, limite):
    cab = ["n", "CPU A (ms)", "CPU B (ms)", "CPU C (ms)", "Mem. A (KiB)", "Mem. B (KiB)", "Mem. C (KiB)"]
    lineas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for n in sorted(datos):
        d = datos[n]
        fila = [str(n), celda_cpu(d.get("A"), limite), celda_cpu(d["B"], limite), celda_cpu(d["C"], limite),
                celda_mem(d.get("A")), celda_mem(d["B"]), celda_mem(d["C"])]
        lineas.append("| " + " | ".join(fila) + " |")
    return "\n".join(lineas)


def tabla_operaciones(datos):
    cab = ["n", "Llamadas A", "Celdas B", "Celdas C", "Celdas B / Celdas C", "Longitud LCS"]
    lineas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for n in sorted(datos):
        d = datos[n]
        a_ops = num(d["A"]["ops"]) if d["A"]["ops"] is not None else "—"
        ratio = cifras(d["B"]["ops"] / d["C"]["ops"], 3) if d["C"]["ops"] else "—"
        lineas.append("| " + " | ".join([str(n), a_ops, num(d["B"]["ops"]), num(d["C"]["ops"]),
                                          ratio, num(d["C"]["lon"])]) + " |")
    return "\n".join(lineas)


def dibujar(datos, limite, ruta_png):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no está instalado: se omite la gráfica.")
        return False

    estilo = {"A": ("#d55e00", "x", ":"), "B": ("#0072b2", "s", "-"), "C": ("#009e73", "o", "--")}
    nombres = {"A": "A (recursiva)", "B": "B (Hirschberg)", "C": "C (prog. dinámica)"}
    tamanos = sorted(datos)

    plt.rcParams.update({"font.size": 9})
    fig, (ax_t, ax_m) = plt.subplots(1, 2, figsize=(6.3, 2.9), constrained_layout=True)

    for v in "ABC":
        color, marcador, linea = estilo[v]
        xs_t = [n for n in tamanos if datos[n][v]["estado"] == "ok"]
        ax_t.plot(xs_t, [datos[n][v]["cpu_s"] for n in xs_t], color=color, marker=marcador,
                  linestyle=linea, markersize=4, linewidth=1.2, label=nombres[v])
        xs_m = [n for n in xs_t if datos[n][v]["pico"] is not None]
        ax_m.plot(xs_m, [datos[n][v]["pico"] / 1024 for n in xs_m], color=color, marker=marcador,
                  linestyle=linea, markersize=4, linewidth=1.2, label=nombres[v])

    # Versión A: primer tamaño que superó el límite de tiempo
    agotados = [n for n in tamanos if datos[n]["A"]["estado"] == "timeout"]
    if agotados and limite:
        ax_t.plot(agotados[0], limite, marker="^", color=estilo["A"][0], markerfacecolor="none", linestyle="none")
        ax_t.annotate(f"> {limite:g} s", (agotados[0], limite), textcoords="offset points",
                      xytext=(5, -9), color=estilo["A"][0], fontsize=8)

    for ax, titulo, etiqueta in ((ax_t, "Tiempo de CPU", "s"), (ax_m, "Pico de memoria", "KiB")):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Longitud n de cada cadena")
        ax.set_ylabel(f"{titulo} ({etiqueta})")
        ax.set_title(titulo)
        ax.grid(True, which="both", alpha=0.25)
    ax_m.legend(frameon=False, loc="upper left")
    fig.savefig(ruta_png, dpi=200)
    plt.close(fig)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--salida", default="resultados")
    args = ap.parse_args(argv)

    datos = leer(os.path.join(args.salida, "resultados.csv"))
    limite = limite_a(args.salida)

    texto = ["# Tablas de resultados\n",
             "**Tabla principal** (CPU: mediana de las repeticiones; memoria: pico adicional medido con tracemalloc).\n",
             tabla_principal(datos, limite),
             "\n— : no ejecutada (el tamaño anterior ya superó el límite de tiempo). "
             f"> {num(limite * 1000) if limite else '?'} : no terminó en el límite de tiempo.\n",
             "**Operaciones** (llamadas recursivas en A; celdas de tabla evaluadas en B y C).\n",
             tabla_operaciones(datos), ""]
    ruta_md = os.path.join(args.salida, "tablas.md")
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(texto))
    print(f"Tablas guardadas en {ruta_md}")

    if dibujar(datos, limite, os.path.join(args.salida, "grafica_comparativa.png")):
        print(f"Gráfica guardada en {os.path.join(args.salida, 'grafica_comparativa.png')}")


if __name__ == "__main__":
    main()
