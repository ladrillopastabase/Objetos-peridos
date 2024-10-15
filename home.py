import datetime
import random
import json
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import os
import requests
import base64
from supabase import create_client, Client

#from dotenv import load_dotenv
#load_dotenv("C:/Users/ferna/OneDrive/Escritorio/Ferna/Programación/Pagina Objetos perdidos/variables.env")
#imagebbkey: str = os.environ.get("IMAGEBB_KEY")
imagebbkey: str = st.secrets["IMAGEBB_KEY"]
print("Pagina inicializada correctamente!")

#url: str = os.environ.get("SUPABASE_URL")
#key: str = os.environ.get("SUPABASE_KEY")
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
print("Conexión base de datos realizada correctamente!")

#navegacion

# Mostrar el titulo de la pagina
st.set_page_config(page_title="Objetos perdidos", page_icon="🎫")
st.title("🎫 Objetos Perdidos")
st.write(
    """
    Esta página permite a los usuarios identificar los objetos perdidos que no han sido reclamados actualmente.
    """
)

# resutados en existencia
st.header("Objetos en existencia")

#realiza query sobre los objetos
raw_data = supabase.table("objetos").select("*").execute()
df = pd.DataFrame(raw_data.data) #convertir la query en dataframe
df['item'] = df['item'].apply(json.loads) # Convertir la columna 'item' de JSON a diccionario
item_df = pd.json_normalize(df['item']) # Expandir la columna 'item' en múltiples columnas
result_df = pd.concat([df[['id']], item_df], axis=1) # Concatenar el DataFrame original con el DataFrame expandido

print(result_df)

# Dividir el DataFrame en grupos de 3 elementos
num_columns = 3
num_rows = len(result_df)

# Dividir el DataFrame en grupos de 3 elementos, comenzando desde el último
for start in range(len(result_df), 0, -num_columns):
    cols = st.columns(num_columns)
    for i, col in enumerate(cols):
        index = start - i - 1
        if index >= 0:
            row = result_df.iloc[index]
            with col:
                container = st.container(border=True)
                container.image(row['item_image_url'])
                container.markdown(f'''{row['item_name']}  
                                   :red[Estado:] {row['item_status']}''')
                container.caption(f"Descripción: {row['item_description']}")
                container.caption(f"Fecha: {row['item_in']}")
