from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "ProyectoGUIFuentes"))

from minpol.io_utils import parse_mpl_file, write_dzn_file
from minpol.minizinc_runner import run_minizinc_model
from minpol.solver import solve_exact


def main() -> int:
    parser = argparse.ArgumentParser(description="Resuelve una instancia MinPol")
    parser.add_argument("input_file", help="Ruta al archivo .mpl")
    parser.add_argument("--dzn-out", help="Ruta del archivo .dzn a generar")
    parser.add_argument("--json-out", help="Ruta del archivo .json para guardar la solucion")
    parser.add_argument("--prefer-minizinc", action="store_true", help="Intentar MiniZinc antes del solver Python")
    args = parser.parse_args()

    instance = parse_mpl_file(args.input_file)
    if args.dzn_out:
        write_dzn_file(instance, args.dzn_out)

    if args.prefer_minizinc:
        try:
            solution = run_minizinc_model(ROOT_DIR / "Proyecto.mzn", args.dzn_out or ROOT_DIR / "DatosProyecto" / "DatosProyecto.dzn")
        except Exception:
            solution = solve_exact(instance)
    else:
        solution = solve_exact(instance)

    payload = {
        "method": solution.method,
        "polarization": solution.polarization,
        "total_cost": solution.total_cost,
        "total_movements": solution.total_movements,
        "median_index": solution.median_index + 1,
        "final_distribution": solution.final_distribution,
        "transfers": solution.transfers,
    }

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    print(solution.to_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
