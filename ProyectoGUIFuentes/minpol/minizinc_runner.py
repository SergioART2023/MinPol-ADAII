from __future__ import annotations

import ast
import shutil
import subprocess
from pathlib import Path

from .models import Solution


def _parse_output(raw_output: str) -> Solution:
    payload: dict[str, object] = {}
    rows: list[list[int]] = []
    for line in raw_output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("----------") or stripped.startswith("=========="):
            continue
        if stripped.startswith("fila_"):
            _, raw_value = stripped.split("=", 1)
            rows.append(list(ast.literal_eval(raw_value.strip())))
            continue
        if "=" in stripped:
            key, raw_value = stripped.split("=", 1)
            payload[key.strip()] = raw_value.strip()

    return Solution(
        transfers=rows,
        final_distribution=list(ast.literal_eval(str(payload["distribucion_final"]))),
        polarization=float(payload["polarizacion"]),
        total_cost=float(payload["costo_total"]),
        total_movements=int(payload["movimientos_totales"]),
        median_index=int(payload["indice_mediana"]) - 1,
        method="minizinc",
    )


def run_minizinc_model(model_path: str | Path, data_path: str | Path) -> Solution:
    executable = shutil.which("minizinc")
    if executable is None:
        raise FileNotFoundError("No se encontro el ejecutable de MiniZinc en el PATH")

    process = subprocess.run(
        [executable, str(model_path), str(data_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "La ejecucion de MiniZinc fallo")
    return _parse_output(process.stdout)
