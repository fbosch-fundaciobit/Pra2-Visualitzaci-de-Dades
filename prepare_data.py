import subprocess
import sys

# Calcula la puntuació normalitzada dels fertilitzants, i calcula mitjanes de condicions ambientals.
subprocess.run([sys.executable, "calcul_fertilitzant_normalitzat.py"])
# Genera CSV relacionats amb la producció vs fertilitzants.
subprocess.run([sys.executable, "produccio_vs_fertilitzant.py"])
# Genera CSV amb el valors de producció ajustats per "anular" l'efecte dels fertilitzants.
subprocess.run([sys.executable, "produccio_vs_fertilitzant_ajustat.py"])

#Anàlisis individuals de producció vs temperatures a diferents periodes de temps.
#subprocess.run([sys.executable, "produccio_vs_temp_max_30dies.py"])
#subprocess.run([sys.executable, "produccio_vs_temp_max_120dies.py"])
#subprocess.run([sys.executable, "produccio_vs_temp_min_30dies.py"])
#subprocess.run([sys.executable, "produccio_vs_temp_min_120dies.py"])

# Aquests scripts generen CSVs especifics per certs gràfics. Calculant mitjanes i rotant files i columnes.
# per facilitar la creació dels gràfics amb Flourish.

#Genera CSV per a gràfics d'àrea.
subprocess.run([sys.executable, "area_chart_rh.py"])
#Genera CSV per a gràfics de area segons temperatura.
subprocess.run([sys.executable, "area_chart_temp.py"])
#Genera CSV per als 4 gràfics de línies de prod vs temp maximes i minimes dels primers i darrers 30 dies.
subprocess.run([sys.executable, "produccio_vs_temp_4_periodes.py"])
