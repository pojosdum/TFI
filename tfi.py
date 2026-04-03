# ################################################## #
# # PROJECT : TFI                                  # #
# # AUTHOR  : pojosdum                             # #
# # DATE    : 2026-04-03                           # #
# ################################################## #



import requests
from datetime import datetime
import csv
import os

def calculate_tfi():
    #API del Ministerio
    API_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    print("Obteniendo datos del Ministerio...")
    
    response = requests.get(API_URL)
    if response.status_code != 200:
        print(f"Error obteniendo datos: HTTP {response.status_code}")
        return
        
    data = response.json()
    stations = data.get("ListaEESSPrecio", [])
    
    #Filtrando para Torrent (46900) y Xirivella (46950)
    target_postal_codes = ["46900", "46950"]
    local_stations = [s for s in stations if s.get("C.P.") in target_postal_codes]
    
    #Peso de las distintas gasolineras en mi índice
    basket = {
        # Gasolineras de Torrent
        "CALLE CAMI REIAL, 4": {"name": "Cepsa Torrent", "weight": 0.15, "base_price": 1.65},
        "CALLE FERNANDO FURIO R, 4": {"name": "Repsol Torrent", "weight": 0.15, "base_price": 1.65},
        "CALLE MAS DEL JUTGE, 2": {"name": "Ballenoil Torrent", "weight": 0.20, "base_price": 1.45},
        "PARTIDA TOLL L'ALBERCA, 1": {"name": "GasExpress Torrent", "weight": 0.20, "base_price": 1.45},
        
        # --- Xirivella Stations ---
        "AV  CAMI NOU, 180": {"name": "Full & Go Xirivella", "weight": 0.15, "base_price": 1.45}, # Note the double space!
        "CALLE RAJOLAR, EL, 4": {"name": "Plenergy Xirivella", "weight": 0.15, "base_price": 1.45}
    }
    
    current_weighted_sum = 0
    base_weighted_sum = 0
    found_stations = 0
    
    print("\n--- Daily Station Prices (Gasolina 95) ---")
    
    #Procesado de los datos para el cálculo del índice
    for station in local_stations:
        address = station.get("Dirección")
        
        if address in basket:
            #gasolina pal polito
            price_str = station.get("Precio Gasolina 95 E5", "0")
            
            #Sin dato continúa
            if not price_str or price_str == "0":
                continue
                
            found_stations += 1
            
            #Conversión de strings de la API
            price_str = price_str.replace(",", ".")
            current_price = float(price_str)
            
            weight = basket[address]["weight"]
            base_price = basket[address]["base_price"]
            
            current_weighted_sum += (current_price * weight)
            base_weighted_sum += (base_price * weight)
            
            print(f"[{basket[address]['name']}] {address}: {current_price} €/L")

    #Índice final
    if found_stations == len(basket):
        tfi_index = (current_weighted_sum / base_weighted_sum) * 100
        print(f"\n=========================================")
        print(f" Torrent(e) Fuel Index (TFI)")
        print(f" Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f" Value: {tfi_index:.2f}")
        print(f"=========================================\n")
    else:
        print(f"\nWarning: Solo {found_stations} de {len(basket)} gasolineras.")

if __name__ == "__main__":
    calculate_tfi()
