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
def obtener_precios_shein():
    url = "https://us.shein.com/Women-Clothing-c-2035.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    productos = []
    for item in soup.select('.S-product-item__info'):
        nombre = item.select_one('.S-product-item__name').text.strip()
        precio = item.select_one('.S-product-item__price').text.strip().replace('$', '')
        enlace = item.find('a', href=True)['href']
        productos.append({
            "Fecha": datetime.now().strftime('%Y-%m-%d'),
            "Producto": nombre,
            "Precio (USD)": float(precio),
            "Enlace": f"https://us.shein.com{enlace}"
        })
    
    return pd.DataFrame(productos)

# Guardar los datos en un archivo CSV
def guardar_datos_csv(datos):
    archivo = "precios_shein.csv"
    if not os.path.exists(archivo):
        datos.to_csv(archivo, index=False)
    else:
        datos.to_csv(archivo, mode='a', header=False, index=False)

# Función para generar el dashboard
def generar_dashboard():
    archivo = "precios_shein.csv"
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
    app.run_server(debug=True)

# Función principal: combinar todo
def tarea_semanal():
    print("Ejecutando scraping...")
    datos = obtener_precios_shein()
    guardar_datos_csv(datos)
    print("Datos guardados en CSV.")
    generar_dashboard()

# Programar tarea semanal
schedule.every().sunday.at("09:00").do(tarea_semanal)

print("Automatización configurada. Esperando ejecución semanal...")
while True:
    schedule.run_pending()
    time.sleep(1)

