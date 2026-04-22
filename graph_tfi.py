# ################################################## #
# # PROJECT : TFI                                  # #
# # AUTHOR  : pojosdum                             # #
# # DATE    : 2026-04-03                           # #
# ################################################## #



import csv
from datetime import datetime
import matplotlib.pyplot as plt

def plot_index():
    
    csv_file = r"C:\Users\Omobe\OneDrive\Documentos\AaUniversity\REPOS\TFI\historico_tfi.csv"
    
    dates = []
    values = []

    fecha_inicio = datetime.strptime('2026-04-01', '%Y-%m-%d')

    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  
            
            for row in reader:
                if row: 
                    date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                    
                    if date_obj >= fecha_inicio:
                        dates.append(date_obj)
                        values.append(float(row[1]))
    except FileNotFoundError:
        print(f"Error: No se encontró {csv_file}")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

    if not dates:
        print("No hay datos para mostrar a partir de la fecha seleccionada.")
        return
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(dates, values, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=6, label="Valor Diario TFI")
    
    plt.axhline(y=102, color='red', linestyle='--', alpha=0.5, label='Baseline (102)')

    plt.title('TFI', fontsize=14, fontweight='bold')
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Valor del Índice ', fontsize=12)
    
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.legend()
    
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    
    print("Abriendo gráfico")
    plt.show()

if __name__ == "__main__":
    plot_index()