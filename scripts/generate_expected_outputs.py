from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "ProyectoGUIFuentes"))

from minpol.io_utils import parse_mpl_file, write_dzn_file
from minpol.solver import solve_exact


def main() -> int:
    rows: list[dict[str, object]] = []
    for folder in [ROOT_DIR / "DatosProyecto", ROOT_DIR / "MisInstancias"]:
        for input_path in sorted(folder.glob("*.mpl")):
            instance = parse_mpl_file(input_path)
            write_dzn_file(instance, input_path.with_suffix(".dzn"))

            start = time.perf_counter()
            solution = solve_exact(instance)
            elapsed_ms = (time.perf_counter() - start) * 1000

            payload = {
                "instance": input_path.name,
                "polarization": solution.polarization,
                "total_cost": solution.total_cost,
                "total_movements": solution.total_movements,
                "median_index": solution.median_index + 1,
                "final_distribution": solution.final_distribution,
                "transfers": solution.transfers,
                "method": solution.method,
                "time_ms": elapsed_ms,
            }
            input_path.with_suffix(".expected.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=True),
                encoding="utf-8",
            )

            rows.append(
                {
                    "instancia": input_path.name,
                    "n": instance.n,
                    "m": instance.m,
                    "polarizacion": f"{solution.polarization:.6f}",
                    "costo_total": f"{solution.total_cost:.6f}",
                    "movimientos": solution.total_movements,
                    "tiempo_ms": f"{elapsed_ms:.3f}",
                }
            )

    report_path = ROOT_DIR / "docs" / "resultados_pruebas.csv"
    with report_path.open("w", encoding="utf-8", newline="") as handler:
        writer = csv.DictWriter(
            handler,
            fieldnames=["instancia", "n", "m", "polarizacion", "costo_total", "movimientos", "tiempo_ms"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
