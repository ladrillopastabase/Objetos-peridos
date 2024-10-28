from datetime import datetime, timedelta
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
#Inicializacion de variables
load_dotenv("C:/Users/ferna/OneDrive/Escritorio/Ferna/Programación/Pagina Objetos perdidos/variables.env")

#imagebb
imagebbkey: str = os.environ.get("IMAGEBB_KEY")
print("Pagina inicializada correctamente!")

#supabade
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
print("Conexión base de datos realizada correctamente!")

#Inicio de sesión
user: str = os.environ.get("USER")
password: str = os.environ.get("PASSWORD")

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


# Create user_state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {
        'name_surname': '',
        'password': '',
        'logged_in': False,
    }

#checkeo inicio de sesion
if not st.session_state.user_state['logged_in']:
    # Create login form
    st.header("Log in")
    st.write('Por favor inicie sesión')
    login_user = st.text_input("Usuario")
    login_password = st.text_input('Password', type='password')
    submit = st.button('Login')

    # Check if user is logged in
    if submit:
        if login_user == user:
            if login_password == password:
                st.session_state.user_state['user'] = login_user
                st.session_state.user_state['password'] = password
                st.session_state.user_state['logged_in'] = True
                st.write('You are logged in')
                st.rerun()
            else:
                st.write('Invalid username or password')
        else:
            st.error('User not found')


#Aplicación una vez iniciada la sesión
elif st.session_state.user_state['logged_in']:
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
        item_category = st.selectbox("Categoría", ["Tecnología", "Vestuario", "Comida", "Útiles", "Otros"])
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
            "item_category": item_category,
            "item_finder": item_finder,
            "item_owner": "Desconocido",
            "item_owner_rut": "",
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

    # Convertir las fechas de 'item_in' a tipo datetime
    result_df['item_in'] = pd.to_datetime(result_df['item_in'])

    # Extraer el mes y año para agrupación
    result_df['period'] = result_df['item_in'].dt.to_period('M')

    # Agrupar por mes y contar objetos
    lost_items_by_month = result_df.groupby('period').size().reset_index(name='count')
    print(lost_items_by_month)
    
    # Convertir la columna 'period' a timestamp
    lost_items_by_month['period'] = lost_items_by_month['period'].dt.to_timestamp()


    

    def compare_periods(df):
        # Verificar si el DataFrame tiene al menos 2 filas
        if len(df) >= 2:
            periodo_anterior = df["count"].iloc[-2]
        elif len(df) == 1:
            periodo_anterior = 0
        
        # Obtener el último periodo y su conteo
        ultimo_periodo = df["count"].iloc[-1]
        resultado = ultimo_periodo - periodo_anterior

        return int(resultado)


    objetos_mes = compare_periods(lost_items_by_month)




    # Show some metrics and charts about the ticket.
    st.header("Estadísticas")

    # Show metrics side by side using `st.columns` and `st.metric`.
    col1, col2, col3 = st.columns(3)
    num_open_tickets = len(result_df[result_df["item_status"] == "Perdido"])
    col1.metric(label="Objetos Perdidos este Mes", value=num_open_tickets, delta=objetos_mes)
    col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
    col3.metric(label="Average resolution time (hours)", value=16, delta=2)

    # Show two Altair charts using `st.altair_chart`.
    st.write("")
    st.write("##### Objetos perdidos por mes")
    

    # Crear el gráfico con Altair
    chart = alt.Chart(lost_items_by_month).mark_bar().encode(
        x=alt.X('period:T', axis=alt.Axis(title='Período')),  # Especificamos el formato de fecha
        y=alt.Y('count:Q', axis=alt.Axis(title='Conteo'))
    )

    st.altair_chart(chart, use_container_width=True, theme="streamlit")



    #Objetos

    st.header("Objetos en existencia")
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

    st.dataframe(result_df, use_container_width=True, hide_index=True)













