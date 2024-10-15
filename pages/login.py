import datetime
import random
import json
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os

from dotenv import load_dotenv
load_dotenv("C:/Users/ferna/OneDrive/Escritorio/Ferna/Programación/Pagina Objetos perdidos/variables.env")
user: str = os.environ.get("USER")
password: str = os.environ.get("PASSWORD")

st.dialog("hola")

if "role" not in st.session_state:
    st.session_state.role = None

st.header("Log in")

with st.form("login"):
    input_user = st.text_input("Usuario")
    input_password = st.text_input("Contraseña")
    input_button = st.form_submit_button("Submit")

if input_button:
    if input_user == user:
        if input_password == password:
            print("Sesion iniciada correctamente")
            st.switch_page("pages/dashboard.py")
        else:
            st.write("Contraseña incorrecta")
    else:
        st.write("Usuario incorrecto")