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

edited_df = result_df[["item_category"]].copy()

print(edited_df)

st.dataframe(result_df, use_container_width=True, hide_index=True)


st.header("Objetos en existencia")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="item_category:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
