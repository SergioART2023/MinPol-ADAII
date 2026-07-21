from __future__ import annotations

from pathlib import Path
import json

from .models import ProblemInstance


def _parse_int_list(raw_value: str) -> list[int]:
    return [int(token.strip()) for token in raw_value.split(",") if token.strip()]


def _parse_float_list(raw_value: str) -> list[float]:
    return [float(token.strip()) for token in raw_value.split(",") if token.strip()]


def parse_mpl_text(content: str) -> ProblemInstance:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) < 8:
        raise ValueError("El archivo .mpl no contiene suficientes lineas")

    n = int(lines[0])
    m = int(lines[1])
    initial_distribution = _parse_int_list(lines[2])
    opinion_values = _parse_float_list(lines[3])
    extra_costs = _parse_float_list(lines[4])
    move_costs = [_parse_float_list(lines[5 + index]) for index in range(m)]
    max_total_cost = float(lines[5 + m])
    max_movements = int(lines[6 + m])

    instance = ProblemInstance(
        n=n,
        m=m,
        initial_distribution=initial_distribution,
        opinion_values=opinion_values,
        extra_costs=extra_costs,
        move_costs=move_costs,
        max_total_cost=max_total_cost,
        max_movements=max_movements,
    )
    instance.validate()
    return instance


def parse_mpl_file(file_path: str | Path) -> ProblemInstance:
    return parse_mpl_text(Path(file_path).read_text(encoding="utf-8"))


def write_dzn_file(instance: ProblemInstance, file_path: str | Path) -> Path:
    target_path = Path(file_path)
    move_rows = " |\n     | ".join(
        ", ".join(f"{value:g}" for value in row)
        for row in instance.move_costs
    )
    content = "\n".join(
        [
            f"n = {instance.n};",
            f"m = {instance.m};",
            "p = [" + ", ".join(str(value) for value in instance.initial_distribution) + "];",
            "v = [" + ", ".join(f"{value:g}" for value in instance.opinion_values) + "];",
            "ce = [" + ", ".join(f"{value:g}" for value in instance.extra_costs) + "];",
            "c = [| " + move_rows + " |];",
            f"ct = {instance.max_total_cost:g};",
            f"maxM = {instance.max_movements};",
            "",
        ]
    )
    target_path.write_text(content, encoding="utf-8")
    return target_path


def solution_to_json(solution: object) -> str:
    return json.dumps(solution, indent=2, ensure_ascii=True)

