import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import schedule
import time
import dash
from dash import dcc, html
import plotly.express as px

# Función para obtener datos de Shein
def obtener_precios_shein(palabra_clave="vestidos"):
    url = f"https://us.shein.com/search?keyword={palabra_clave}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    productos = []
    for item in soup.select('.S-product-item__info'):
        try:
            nombre = item.select_one('.S-product-item__name').text.strip()
            precio = item.select_one('.S-product-item__price-current').text.strip().replace('$', '')
            productos.append({
                'Producto': nombre,
                'Precio (USD)': float(precio),
                'Fecha': datetime.now().strftime('%Y-%m-%d')
            })
        except AttributeError:
            continue  # Ignorar productos incompletos
    
    return pd.DataFrame(productos)

# Guardar los datos en un archivo CSV
def guardar_datos_csv(dataframe, archivo='shein_precios.csv'):
    try:
        # Cargar datos existentes si el archivo ya existe
        if os.path.exists(archivo):
            datos_existentes = pd.read_csv(archivo)
            datos_totales = pd.concat([datos_existentes, dataframe], ignore_index=True)
        else:
            datos_totales = dataframe
        # Guardar todos los datos combinados en el archivo CSV
        datos_totales.to_csv(archivo, index=False)
        print(f"Datos guardados en {archivo}")
    except Exception as e:
        print(f"Error al guardar datos: {e}")

# Función para generar el dashboard
def generar_dashboard():
    archivo = "shein_precios.csv"
    if not os.path.exists(archivo):
        print("No hay datos disponibles para generar el dashboard.")
        return
    
    datos = pd.read_csv(archivo)
    fig = px.line(datos, x="Fecha", y="Precio (USD)", color="Producto",
                  title="Tendencia de Precios de Ropa en Shein")
    
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("Dashboard de Precios - Shein"),
        dcc.Graph(figure=fig)
    ])
    app.run_server(debug=False)

# Función principal: combinar todo
def tarea_semanal():
    print("Ejecutando scraping...")
    datos = obtener_precios_shein()
    guardar_datos_csv(datos)
    print("Datos guardados en CSV.")
    print("Generando dashboard interactivo...")
    generar_dashboard()

# Programar tarea semanal
schedule.every().sunday.at("09:00").do(tarea_semanal)

print("Automatización configurada. Esperando ejecución semanal...")
while True:
    schedule.run_pending()
    time.sleep(1)
