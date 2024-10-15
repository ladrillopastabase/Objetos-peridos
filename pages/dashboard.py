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

from dotenv import load_dotenv
load_dotenv("C:/Users/ferna/OneDrive/Escritorio/Ferna/Programación/Pagina Objetos perdidos/variables.env")
imagebbkey: str = os.environ.get("IMAGEBB_KEY")
print("Pagina inicializada correctamente!")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
print("Conexión base de datos realizada correctamente!")


#Funcion para cargar imagenes a imagebb
def upload_image_to_imgbb(api_key, image):
    # The API endpoint
    url = "https://api.imgbb.com/1/upload"
    payload = {
            "key": api_key,
            "image": base64.b64encode(image),  # Read image in binary format
        }
    # Send the POST request
    response_image = requests.post(url, data=payload)
    return response_image.json()





# Mostrar ek titulo de la pagina
st.set_page_config(page_title="Objetos perdidos", page_icon="🎫")
st.title("🎫 Objetos Perdidos")
st.write(
    """
    Esta página permite a los usuarios identificar los objetos perdidos que no han sido reclamados actualmente.
    """
)

# Show a section to add a new ticket.
st.header("Añadir un objeto")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
#formulario
with st.form("add_ticket_form"):
    item_name = st.text_input("Nombre del objeto")
    item_finder = st.text_input("Nombre de la persona que lo encontró")
    item_description = st.text_area("Descripción")
    item_image = st.file_uploader("Subir imagen", type= ['png', 'jpg'] )
    submitted = st.form_submit_button("Submit")

#boton formulario
if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.

    imagebb_response = upload_image_to_imgbb(imagebbkey, item_image.getvalue()) # Carga de imagen a image bb
    #imagebb_data = json.loads(imagebb_response)

    data_submit = {
        "item_name": item_name,
        "item_finder": item_finder,
        "item_owner": "Desconocido",
        "item_description": item_description,
        "item_status": "Perdido",
        "item_image_url": imagebb_response["data"]["url"],
        "item_in": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_out": ""
    }

    print(json.dumps(data_submit))

    try:
        user = supabase.auth.sign_in_with_password({"email": "objetosperdidosdaf@gmail.com", "password": "Objetosperdidos.1234"})
        print("Loggeado correctamente!")
    except APIError:
        print("Error")

    # Enviar info a supabase
    insert = (supabase.table("objetos").insert({"item": json.dumps(data_submit)}).execute())

    # Show a little success message.
    st.write("Ticket submitted! Here are the ticket details:", data_submit)

    supabase.auth.sign_out()


# resutados en existencia
st.header("Objetos en existencia")

#realiza query sobre los objetos
raw_data = supabase.table("objetos").select("*").execute()

#convertir la query en dataframe
df = pd.DataFrame(raw_data.data)

# Convertir la columna 'item' de JSON a diccionario
df['item'] = df['item'].apply(json.loads)

# Expandir la columna 'item' en múltiples columnas
item_df = pd.json_normalize(df['item'])

# Concatenar el DataFrame original con el DataFrame expandido
result_df = pd.concat([df[['id']], item_df], axis=1)

print(result_df)

st.dataframe(result_df, use_container_width=True, hide_index=True)

