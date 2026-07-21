MinPol - Analisis de Algoritmos II

Contenido:
- Proyecto.mzn: Modelo generico en MiniZinc.
- DatosProyecto: Ejemplo base del enunciado y archivo DatosProyecto.dzn generado.
- MisInstancias: Cinco instancias creadas como reto para otros grupos del curso para sus proyectos con sus archivos .dzn y .expected.json.
- ProyectoGUIFuentes: Código fuente de la interfaz grafica y del solver de respaldo.
- scripts/generate_expected_outputs.py: Regenera archivos .dzn, .expected.json y docs/resultados_pruebas.csv.
- tests: pruebas unitarias.

Requisitos:
- Python 3.11 o superior.
- MiniZinc instalado y agregado al PATH si se desea ejecutar el modelo desde la GUI.

Pasos a seguir:

1. Crear un entorno virtual:
   py -m venv .venv
2. Activarlo en PowerShell:
   .\.venv\Scripts\Activate.ps1
3. Ejecutar pruebas:
   $env:PYTHONPATH='ProyectoGUIFuentes'
   python -m unittest discover -s tests -v

4. Ejecutar la interfaz grafica:
   $env:PYTHONPATH='ProyectoGUIFuentes'
   python ProyectoGUIFuentes/main.py

5. Regenerar resultados esperados:
   $env:PYTHONPATH='ProyectoGUIFuentes'
   python scripts/generate_expected_outputs.py

Si se desea forzar MiniZinc en consola para una instancia:
   $env:PYTHONPATH='ProyectoGUIFuentes'
   python scripts/solve_instance.py DatosProyecto/ejemplo_seccion_24.mpl --dzn-out DatosProyecto/DatosProyecto.dzn --prefer-minizinc


