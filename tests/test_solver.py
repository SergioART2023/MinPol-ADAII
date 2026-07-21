from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "ProyectoGUIFuentes"))

from minpol.io_utils import parse_mpl_file, write_dzn_file
from minpol.solver import solve_exact


class SolverTests(unittest.TestCase):
    def test_example_instance_is_feasible(self) -> None:
        instance = parse_mpl_file(ROOT_DIR / "DatosProyecto" / "ejemplo_seccion_24.mpl")
        solution = solve_exact(instance)

        self.assertLessEqual(solution.total_cost, instance.max_total_cost + 1e-9)
        self.assertLessEqual(solution.total_movements, instance.max_movements)
        self.assertEqual(solution.final_distribution, [sum(row[column] for row in solution.transfers) for column in range(instance.m)])
        self.assertEqual([sum(row) for row in solution.transfers], instance.initial_distribution)

    def test_dzn_writer_emits_matrix(self) -> None:
        instance = parse_mpl_file(ROOT_DIR / "DatosProyecto" / "ejemplo_seccion_24.mpl")
        output_path = ROOT_DIR / "docs" / "test_data.dzn"
        write_dzn_file(instance, output_path)
        content = output_path.read_text(encoding="utf-8")

        self.assertIn("c = array2d(1..m, 1..m, [", content)
        self.assertIn("maxM = 18;", content)

    def test_expected_outputs_match_solver(self) -> None:
        for folder in [ROOT_DIR / "DatosProyecto", ROOT_DIR / "MisInstancias"]:
            for input_path in sorted(folder.glob("*.mpl")):
                instance = parse_mpl_file(input_path)
                expected = json.loads(input_path.with_suffix(".expected.json").read_text(encoding="utf-8"))
                solution = solve_exact(instance)

                self.assertAlmostEqual(solution.polarization, expected["polarization"], places=6)
                self.assertAlmostEqual(solution.total_cost, expected["total_cost"], places=6)
                self.assertEqual(solution.total_movements, expected["total_movements"])
                self.assertEqual(solution.final_distribution, expected["final_distribution"])


if __name__ == "__main__":
    unittest.main()