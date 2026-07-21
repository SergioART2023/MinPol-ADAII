from __future__ import annotations

from dataclasses import dataclass
from math import isclose


@dataclass(slots=True)
class ProblemInstance:
    n: int
    m: int
    initial_distribution: list[int]
    opinion_values: list[float]
    extra_costs: list[float]
    move_costs: list[list[float]]
    max_total_cost: float
    max_movements: int

    def validate(self) -> None:
        if self.n <= 0:
            raise ValueError("n debe ser positivo")
        if self.m <= 0:
            raise ValueError("m debe ser positivo")
        if len(self.initial_distribution) != self.m:
            raise ValueError("La distribucion inicial no coincide con m")
        if len(self.opinion_values) != self.m:
            raise ValueError("La lista de valores de opinion no coincide con m")
        if len(self.extra_costs) != self.m:
            raise ValueError("La lista de costos extra no coincide con m")
        if len(self.move_costs) != self.m or any(len(row) != self.m for row in self.move_costs):
            raise ValueError("La matriz de costos debe ser cuadrada de tamano m x m")
        if sum(self.initial_distribution) != self.n:
            raise ValueError("La suma de la distribucion inicial debe ser n")
        if any(value < 0 for value in self.initial_distribution):
            raise ValueError("La distribucion inicial no puede contener negativos")
        if any(cost < 0 for cost in self.extra_costs):
            raise ValueError("Los costos extra no pueden ser negativos")
        if any(cost < 0 for row in self.move_costs for cost in row):
            raise ValueError("Los costos de movimiento no pueden ser negativos")
        if not all(self.opinion_values[index] <= self.opinion_values[index + 1] for index in range(self.m - 1)):
            raise ValueError("Los valores de opinion deben venir ordenados de forma no decreciente")
        for index in range(self.m):
            if not isclose(self.move_costs[index][index], 0.0, abs_tol=1e-9):
                raise ValueError("Los costos diagonales c[i][i] deben ser 0")

    def per_person_cost(self, source: int, target: int) -> float:
        base_cost = self.move_costs[source][target] * (1 + self.initial_distribution[source] / self.n)
        if source != target and self.initial_distribution[target] == 0:
            return base_cost + self.extra_costs[target]
        return base_cost


@dataclass(slots=True)
class Solution:
    transfers: list[list[int]]
    final_distribution: list[int]
    polarization: float
    total_cost: float
    total_movements: int
    median_index: int
    method: str

    def to_text(self) -> str:
        rows = ["[" + ", ".join(str(value) for value in row) + "]" for row in self.transfers]
        lines = [
            f"metodo={self.method}",
            f"polarizacion={self.polarization:.6f}",
            f"costo_total={self.total_cost:.6f}",
            f"movimientos_totales={self.total_movements}",
            f"indice_mediana={self.median_index + 1}",
            "distribucion_final=[" + ", ".join(str(value) for value in self.final_distribution) + "]",
            "matriz_x=",
            *rows,
        ]
        return "\n".join(lines)
