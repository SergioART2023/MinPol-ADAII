from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .io_utils import parse_mpl_file, parse_mpl_text, write_dzn_file
from .minizinc_runner import run_minizinc_model
from .models import ProblemInstance
from .solver import solve_exact


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "DatosProyecto"
MODEL_PATH = ROOT_DIR / "Proyecto.mzn"


class MinPolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MinPol - Proyecto ADA II")
        self.root.geometry("1100x760")

        self.n_var = tk.StringVar()
        self.m_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.movements_var = tk.StringVar()

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(container)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="Cargar .mpl", command=self.load_mpl).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Resolver", command=self.solve).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Limpiar", command=self.clear_form).pack(side=tk.LEFT)

        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        for row in [3, 5, 7, 9, 11]:
            form.rowconfigure(row, weight=1)

        self._add_entry(form, "Numero total de personas (n)", self.n_var, 0, 0)
        self._add_entry(form, "Numero de opiniones (m)", self.m_var, 0, 2)
        self._add_entry(form, "Costo total maximo (ct)", self.cost_var, 1, 0)
        self._add_entry(form, "Maximo de movimientos (maxM)", self.movements_var, 1, 2)

        self.initial_text = self._add_text(form, "Distribucion inicial p", 2)
        self.values_text = self._add_text(form, "Valores de opinion v", 4)
        self.extra_text = self._add_text(form, "Costos extra ce", 6)
        self.matrix_text = self._add_text(form, "Matriz de costos c (una fila CSV por linea)", 8)
        self.output_text = self._add_text(form, "Resultado", 10)

    def _add_entry(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=column + 1, sticky="ew", pady=4)

    def _add_text(self, parent: ttk.Frame, label: str, row: int) -> tk.Text:
        ttk.Label(parent, text=label).grid(row=row, column=0, columnspan=4, sticky="w", pady=(8, 4))
        widget = tk.Text(parent, height=5, wrap=tk.WORD)
        widget.grid(row=row + 1, column=0, columnspan=4, sticky="nsew", pady=(0, 8))
        return widget

    def clear_form(self) -> None:
        self.n_var.set("")
        self.m_var.set("")
        self.cost_var.set("")
        self.movements_var.set("")
        for widget in [self.initial_text, self.values_text, self.extra_text, self.matrix_text, self.output_text]:
            widget.delete("1.0", tk.END)

    def load_mpl(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Seleccione el archivo .mpl",
            filetypes=[("Instancias MinPol", "*.mpl"), ("Todos los archivos", "*.*")],
        )
        if not file_path:
            return
        instance = parse_mpl_file(file_path)
        self.populate_form(instance)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Archivo cargado: {file_path}\n")

    def populate_form(self, instance: ProblemInstance) -> None:
        self.n_var.set(str(instance.n))
        self.m_var.set(str(instance.m))
        self.cost_var.set(f"{instance.max_total_cost:g}")
        self.movements_var.set(str(instance.max_movements))
        self._write_text(self.initial_text, ",".join(str(value) for value in instance.initial_distribution))
        self._write_text(self.values_text, ",".join(f"{value:g}" for value in instance.opinion_values))
        self._write_text(self.extra_text, ",".join(f"{value:g}" for value in instance.extra_costs))
        self._write_text(
            self.matrix_text,
            "\n".join(",".join(f"{value:g}" for value in row) for row in instance.move_costs),
        )

    def _write_text(self, widget: tk.Text, content: str) -> None:
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)

    def _build_instance(self) -> ProblemInstance:
        matrix_lines = [line.strip() for line in self.matrix_text.get("1.0", tk.END).splitlines() if line.strip()]
        content = "\n".join(
            [
                self.n_var.get().strip(),
                self.m_var.get().strip(),
                self.initial_text.get("1.0", tk.END).strip(),
                self.values_text.get("1.0", tk.END).strip(),
                self.extra_text.get("1.0", tk.END).strip(),
                *matrix_lines,
                self.cost_var.get().strip(),
                self.movements_var.get().strip(),
            ]
        )
        return parse_mpl_text(content)

    def solve(self) -> None:
        try:
            instance = self._build_instance()
            DATA_DIR.mkdir(exist_ok=True)
            dzn_path = write_dzn_file(instance, DATA_DIR / "DatosProyecto.dzn")
            try:
                solution = run_minizinc_model(MODEL_PATH, dzn_path)
                header = "Modelo ejecutado con MiniZinc.\n"
            except (FileNotFoundError, RuntimeError) as minizinc_error:
                solution = solve_exact(instance)
                header = f"MiniZinc no disponible o fallo: {minizinc_error}\nSe uso el solver exacto de respaldo.\n"

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, header)
            self.output_text.insert(tk.END, f"Archivo DZN generado en: {dzn_path}\n\n")
            self.output_text.insert(tk.END, solution.to_text())
        except Exception as error:
            messagebox.showerror("Error", str(error))


def run_application() -> None:
    root = tk.Tk()
    app = MinPolApp(root)
    sample_path = DATA_DIR / "ejemplo_seccion_24.mpl"
    if sample_path.exists():
        app.populate_form(parse_mpl_file(sample_path))
    root.mainloop()
