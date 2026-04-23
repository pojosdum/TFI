# ################################################## #
# # PROJECT : TFI                                  # #
# # AUTHOR  : pojosdum                             # #
# # DATE    : 2026-04-03                           # #
# ################################################## #



import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from datetime import datetime
import csv
import os

# Adaptador para compatibilidad TLS con servidores del gobierno
class LegacyTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

def calculate_tfi():
    # API del Ministerio
    API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    print("Obteniendo datos del Ministerio...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    session = requests.Session()
    session.mount("https://", LegacyTLSAdapter())
    response = session.get(API_URL, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"Error obteniendo datos: HTTP {response.status_code}")
        return
        
    data = response.json()
    stations = data.get("ListaEESSPrecio", [])
    
    # Filtrando para Torrent (46900) y Xirivella (46950)
    target_postal_codes = ["46900", "46950"]
    local_stations = [s for s in stations if s.get("C.P.") in target_postal_codes]
    
    # Peso de las distintas gasolineras en mi índice
    basket = {
        # Gasolineras de Torrent
        "CALLE CAMI REIAL, 4": {"name": "Cepsa Torrent", "weight": 0.15, "base_price": 1.65},
        "CALLE FERNANDO FURIO R, 4": {"name": "Repsol Torrent", "weight": 0.15, "base_price": 1.65},
        "CALLE MAS DEL JUTGE, 2": {"name": "Ballenoil Torrent", "weight": 0.20, "base_price": 1.45},
        "PARTIDA TOLL L'ALBERCA, 1": {"name": "GasExpress Torrent", "weight": 0.20, "base_price": 1.45},
        
        # Gasolineras de Xirivella
        "AV  CAMI NOU, 180": {"name": "Full & Go Xirivella", "weight": 0.15, "base_price": 1.45},
        "CALLE RAJOLAR, EL, 4": {"name": "Plenergy Xirivella", "weight": 0.15, "base_price": 1.45}
    }
    
    current_weighted_sum = 0
    base_weighted_sum = 0
    found_stations = 0
    
    print("\nPrecio diario gasolina")
    
    # Procesado de los datos para el cálculo del índice
    for station in local_stations:
        address = station.get("Dirección")
        
        if address in basket:
            # Gasolina pal polito
            price_str = station.get("Precio Gasolina 95 E5", "0")
            
            # Sin dato continúa
            if not price_str or price_str == "0":
                continue
                
            found_stations += 1
            
            # Conversión de strings de la API
            price_str = price_str.replace(",", ".")
            current_price = float(price_str)
            
            weight = basket[address]["weight"]
            base_price = basket[address]["base_price"]
            
            current_weighted_sum += (current_price * weight)
            base_weighted_sum += (base_price * weight)
            
            print(f"[{basket[address]['name']}] {address}: {current_price} €/L")

    # Índice final
    if found_stations == len(basket):
        tfi_index = (current_weighted_sum / base_weighted_sum) * 100
        print(f"\n=========================================")
        print(f" Torrent(e) Fuel Index (TFI)")
        print(f" Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f" Value: {tfi_index:.2f}")
        print(f"=========================================\n")
    
    # Guardado de los datos en CSV
        csv_file = r"C:\Users\Omobe\OneDrive\Documentos\AaUniversity\REPOS\TFI\historico_tfi.csv"
        file_exists = os.path.isfile(csv_file)
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        already_logged = False
        if file_exists:
            with open(csv_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == today_str:
                        already_logged = True
                        break
        
        if not already_logged:
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Date", "TFI Value"]) 
            
                writer.writerow([today_str, f"{tfi_index:.2f}"])
                print(f"Datos casados a {csv_file}")
        else:
            print(f"Ya se ha registrado el TFI para hoy {today_str}")
    else:
        print(f"\nWarning: Solo {found_stations} de {len(basket)} gasolineras.")

if __name__ == "__main__":
    calculate_tfi()
