from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import inf

from .models import ProblemInstance, Solution


@dataclass(slots=True)
class _State:
    cost: float
    parent_counts: tuple[int, ...] | None
    parent_moves: int | None
    allocation: tuple[int, ...] | None


def _compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    @lru_cache(maxsize=None)
    def build(remaining: int, length: int) -> tuple[tuple[int, ...], ...]:
        if length == 1:
            return ((remaining,),)
        rows: list[tuple[int, ...]] = []
        for first in range(remaining + 1):
            for tail in build(remaining - first, length - 1):
                rows.append((first, *tail))
        return tuple(rows)

    return list(build(total, parts))


def _row_options(instance: ProblemInstance, source: int) -> list[tuple[tuple[int, ...], int, float]]:
    options: list[tuple[tuple[int, ...], int, float]] = []
    for allocation in _compositions(instance.initial_distribution[source], instance.m):
        movements = sum(abs(target - source) * allocation[target] for target in range(instance.m))
        if movements > instance.max_movements:
            continue
        cost = sum(instance.per_person_cost(source, target) * allocation[target] for target in range(instance.m))
        if cost - instance.max_total_cost > 1e-9:
            continue
        options.append((allocation, movements, cost))
    return options


def _prune_frontier(frontier: dict[int, _State]) -> dict[int, _State]:
    pruned: dict[int, _State] = {}
    best_cost = inf
    for movements in sorted(frontier):
        state = frontier[movements]
        if state.cost + 1e-9 < best_cost:
            pruned[movements] = state
            best_cost = state.cost
    return pruned


def _weighted_median_candidates(distribution: list[int]) -> list[int]:
    total_people = sum(distribution)
    half = total_people // 2
    prefix = 0
    candidates: list[int] = []
    for index, amount in enumerate(distribution):
        left = prefix
        right = total_people - prefix - amount
        if left <= half and right <= half:
            candidates.append(index)
        prefix += amount
    return candidates


def _polarization(distribution: list[int], opinion_values: list[float]) -> tuple[float, int]:
    best_value = inf
    best_index = 0
    for median_index in _weighted_median_candidates(distribution):
        median_value = opinion_values[median_index]
        value = sum(
            distribution[index] * abs(opinion_values[index] - median_value)
            for index in range(len(distribution))
        )
        if value + 1e-9 < best_value:
            best_value = value
            best_index = median_index
    return best_value, best_index


def solve_exact(instance: ProblemInstance) -> Solution:
    instance.validate()
    row_options = [_row_options(instance, source) for source in range(instance.m)]
    stage: dict[tuple[int, ...], dict[int, _State]] = {
        tuple(0 for _ in range(instance.m)): {0: _State(cost=0.0, parent_counts=None, parent_moves=None, allocation=None)}
    }
    stages: list[dict[tuple[int, ...], dict[int, _State]]] = [stage]

    for source, options in enumerate(row_options):
        next_stage: dict[tuple[int, ...], dict[int, _State]] = {}
        for counts, frontier in stage.items():
            for used_moves, state in frontier.items():
                for allocation, delta_moves, delta_cost in options:
                    new_moves = used_moves + delta_moves
                    new_cost = state.cost + delta_cost
                    if new_moves > instance.max_movements or new_cost - instance.max_total_cost > 1e-9:
                        continue
                    new_counts = tuple(counts[index] + allocation[index] for index in range(instance.m))
                    bucket = next_stage.setdefault(new_counts, {})
                    current = bucket.get(new_moves)
                    if current is None or new_cost + 1e-9 < current.cost:
                        bucket[new_moves] = _State(
                            cost=new_cost,
                            parent_counts=counts,
                            parent_moves=used_moves,
                            allocation=allocation,
                        )
        stage = {counts: _prune_frontier(frontier) for counts, frontier in next_stage.items()}
        stages.append(stage)

    best_distribution: tuple[int, ...] | None = None
    best_moves: int | None = None
    best_cost = inf
    best_polarization = inf
    best_median_index = 0

    for distribution, frontier in stage.items():
        if sum(distribution) != instance.n:
            continue
        polarization, median_index = _polarization(list(distribution), instance.opinion_values)
        selected_moves = min(frontier, key=lambda movement: (frontier[movement].cost, movement))
        selected_cost = frontier[selected_moves].cost
        if polarization + 1e-9 < best_polarization:
            best_distribution = distribution
            best_moves = selected_moves
            best_cost = selected_cost
            best_polarization = polarization
            best_median_index = median_index
        elif abs(polarization - best_polarization) <= 1e-9:
            if selected_cost + 1e-9 < best_cost or (
                abs(selected_cost - best_cost) <= 1e-9 and selected_moves < (best_moves or instance.max_movements + 1)
            ):
                best_distribution = distribution
                best_moves = selected_moves
                best_cost = selected_cost
                best_polarization = polarization
                best_median_index = median_index

    if best_distribution is None or best_moves is None:
        raise ValueError("No se encontro una solucion factible para la instancia")

    transfers_by_source: list[tuple[int, ...]] = [tuple(0 for _ in range(instance.m)) for _ in range(instance.m)]
    current_distribution = best_distribution
    current_moves = best_moves
    for source in range(instance.m - 1, -1, -1):
        state = stages[source + 1][current_distribution][current_moves]
        assert state.allocation is not None
        transfers_by_source[source] = state.allocation
        assert state.parent_counts is not None
        assert state.parent_moves is not None
        current_distribution = state.parent_counts
        current_moves = state.parent_moves

    return Solution(
        transfers=[list(row) for row in transfers_by_source],
        final_distribution=list(best_distribution),
        polarization=best_polarization,
        total_cost=best_cost,
        total_movements=best_moves,
        median_index=best_median_index,
        method="programacion_dinamica_exacta",
    )
